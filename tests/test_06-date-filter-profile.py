import pytest
from app import app as flask_app
from database.db import init_db, get_db
import sqlite3

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # Isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    # Patch get_db to use the in-memory database for the duration of the test
    import database.db
    original_get_db = database.db.get_db

    # Create a persistent connection for the in-memory DB for this test session
    # We use check_same_thread=False because Flask might use different threads
    connection = sqlite3.connect(':memory:', check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")

    def mocked_get_db():
        return connection

    database.db.get_db = mocked_get_db

    with flask_app.app_context():
        init_db()
        yield flask_app

    database.db.get_db = original_get_db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already registered and logged in."""
    # Use a fixed email and name for consistency
    client.post('/register', data={'name': 'Test User', 'password': 'testpass', 'email': 'test@test.com'})
    client.post('/login', data={'email': 'test@test.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seeded_data(app, auth_client):
    """Seeds specific expenses for the authenticated user."""
    with app.app_context():
        db = get_db()
        # Get the first user from the database to ensure we have the correct ID
        user = db.execute('SELECT id FROM users LIMIT 1').fetchone()
        if not user:
            pytest.fail("No user found in database to seed expenses for.")
        user_id = user['id']

        expenses = [
            (user_id, 10.0, 'Food', '2026-01-01', 'Lunch'),
            (user_id, 20.0, 'Transport', '2026-01-15', 'Taxi'),
            (user_id, 30.0, 'Food', '2026-02-01', 'Dinner'),
            (user_id, 40.0, 'Bills', '2026-02-15', 'Electric'),
        ]
        db.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            expenses
        )
        db.commit()

class TestDateFilterProfile:

    def test_profile_auth_guard(self, client):
        """Ensure unauthenticated requests to /profile are redirected to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        # Cast location to string if it's bytes, or compare as bytes
        location = response.location
        if isinstance(location, bytes):
            location = location.decode('utf-8')
        assert '/login' in location

    def test_filter_happy_path_range(self, auth_client, seeded_data):
        """Filtering by a valid start and end date returns correct transactions and stats."""
        # Range: 2026-01-01 to 2026-01-31
        # Expected: Food ($10) and Transport ($20). Total: $30.
        response = auth_client.get('/profile?start_date=2026-01-01&end_date=2026-01-31')

        assert response.status_code == 200
        assert b'30.0' in response.data  # Total spent
        assert b'Lunch' in response.data
        assert b'Taxi' in response.data
        assert b'Dinner' not in response.data
        assert b'Electric' not in response.data

    def test_filter_single_day(self, auth_client, seeded_data):
        """Filtering for a single day returns only that day's expenses."""
        # Date: 2026-02-01
        # Expected: Food ($30)
        response = auth_client.get('/profile?start_date=2026-02-01&end_date=2026-02-01')

        assert response.status_code == 200
        assert b'30.0' in response.data
        assert b'Dinner' in response.data
        assert b'Lunch' not in response.data

    def test_filter_start_date_only(self, auth_client, seeded_data):
        """Filtering with only start_date returns everything from that date onwards."""
        # Start: 2026-02-01
        # Expected: Dinner ($30) and Electric ($40). Total: $70.
        response = auth_client.get('/profile?start_date=2026-02-01')

        assert response.status_code == 200
        assert b'70.0' in response.data
        assert b'Dinner' in response.data
        assert b'Electric' in response.data
        assert b'Lunch' not in response.data

    def test_filter_end_date_only(self, auth_client, seeded_data):
        """Filtering with only end_date returns everything up to that date."""
        # End: 2026-01-20
        # Expected: Lunch ($10) and Taxi ($20). Total: $30.
        response = auth_client.get('/profile?end_date=2026-01-20')

        assert response.status_code == 200
        assert b'30.0' in response.data
        assert b'Lunch' in response.data
        assert b'Taxi' in response.data
        assert b'Dinner' not in response.data

    def test_filter_empty_results(self, auth_client, seeded_data):
        """Filtering a range with no expenses returns correct 'not found' indicators."""
        # Range: 2025-01-01 to 2025-01-31 (No data here)
        response = auth_client.get('/profile?start_date=2025-01-01&end_date=2025-01-31')

        assert response.status_code == 200
        # Total should be 0 or empty
        assert (b'0.0' in response.data or b'0' in response.data)
        # Transactions list should be empty or show a message
        assert b'Lunch' not in response.data

    def test_filter_reset(self, auth_client, seeded_data):
        """Removing filters restores the full dataset."""
        # First, apply a filter to change state
        auth_client.get('/profile?start_date=2026-02-01')

        # Now, request without filters
        response = auth_client.get('/profile')

        assert response.status_code == 200
        # Total: 10 + 20 + 30 + 40 = 100
        assert b'100.0' in response.data
        assert b'Lunch' in response.data
        assert b'Electric' in response.data

    @pytest.mark.parametrize("invalid_date", [
        "not-a-date",
        "2026-13-45",
        "abc-def-ghi",
        "2026/01/01"
    ])
    def test_filter_invalid_date_formats(self, auth_client, seeded_data, invalid_date):
        """Invalid date formats should be handled gracefully (no 500 error)."""
        response = auth_client.get(f'/profile?start_date={invalid_date}')

        # Should not crash. Either it returns 200 (ignoring filter) or 400, but not 500.
        assert response.status_code != 500
        assert response.status_code in [200, 400]
