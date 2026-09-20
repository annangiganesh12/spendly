import pytest
from app import app as flask_app, CATEGORIES
from database.db import init_db, get_db
from datetime import date

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        # We need to override the DATABASE variable in database.db for :memory: to work
        import database.db
        database.db.DATABASE = ':memory:'
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'Test User', 'email': 'test@test.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@test.com', 'password': 'testpass'})
    return client

class TestEditExpense:

    def test_edit_expense_unauthenticated_redirects_to_login(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get('/expenses/1/edit')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_edit_expense_get_success(self, auth_client):
        """User can access the edit page for their own expense with pre-filled data."""
        # Create an expense for the user
        with get_db() as conn:
            user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            user_id = user['id']
            cursor = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, 50.0, 'Food', '2026-01-01', 'Original Desc')
            )
            expense_id = cursor.lastrowid
            conn.commit()

        response = auth_client.get(f'/expenses/{expense_id}/edit')
        assert response.status_code == 200
        assert b'Original Desc' in response.data
        assert b'50.0' in response.data
        assert b'Food' in response.data

    def test_edit_expense_post_success(self, auth_client):
        """User can successfully update their expense."""
        with get_db() as conn:
            user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            user_id = user['id']
            cursor = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, 50.0, 'Food', '2026-01-01', 'Original Desc')
            )
            expense_id = cursor.lastrowid
            conn.commit()

        new_data = {
            'amount': '75.50',
            'category': 'Transport',
            'date': '2026-01-02',
            'description': 'Updated Description'
        }
        response = auth_client.post(f'/expenses/{expense_id}/edit', data=new_data)

        # Verify redirect to profile
        assert response.status_code == 302
        assert '/profile' in response.location

        # Verify DB update
        with get_db() as conn:
            expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
            assert expense['amount'] == 75.50
            assert expense['category'] == 'Transport'
            assert expense['date'] == '2026-01-02'
            assert expense['description'] == 'Updated Description'

    @pytest.mark.parametrize("invalid_data, expected_error", [
        ({'amount': '-10', 'category': 'Food', 'date': '2026-01-01', 'description': 'test'}, b'Amount must be a positive number'),
        ({'amount': '0', 'category': 'Food', 'date': '2026-01-01', 'description': 'test'}, b'Amount must be a positive number'),
        ({'amount': '10', 'category': 'InvalidCat', 'date': '2026-01-01', 'description': 'test'}, b'Invalid category selected'),
        ({'amount': '', 'category': 'Food', 'date': '2026-01-01', 'description': 'test'}, b'Amount, category, and date are required'),
        ({'amount': '10', 'category': '', 'date': '2026-01-01', 'description': 'test'}, b'Amount, category, and date are required'),
        ({'amount': '10', 'category': 'Food', 'date': '', 'description': 'test'}, b'Amount, category, and date are required'),
        ({'amount': 'abc', 'category': 'Food', 'date': '2026-01-01', 'description': 'test'}, b'Invalid amount entered'),
    ])
    def test_edit_expense_validation_errors(self, auth_client, invalid_data, expected_error):
        """Updating with invalid data should show error and stay on page."""
        with get_db() as conn:
            user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            cursor = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user['id'], 50.0, 'Food', '2026-01-01', 'Desc')
            )
            expense_id = cursor.lastrowid
            conn.commit()

        response = auth_client.post(f'/expenses/{expense_id}/edit', data=invalid_data)
        assert response.status_code == 200
        assert expected_error in response.data

    def test_edit_expense_security_cross_user(self, auth_client, client):
        """Verify that one user cannot edit another user's expense."""
        # Setup: User A (auth_client) and User B (new user)
        with get_db() as conn:
            # User B
            conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", ('User B', 'userb@test.com', 'hashed_pass'))
            user_b = conn.execute("SELECT id FROM users WHERE email = 'userb@test.com'").fetchone()
            cursor = conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_b['id'], 100.0, 'Shopping', '2026-01-01', 'User B Item')
            )
            expense_id_b = cursor.lastrowid
            conn.commit()

        # User A attempts to GET User B's expense
        response_get = auth_client.get(f'/expenses/{expense_id_b}/edit')
        assert response_get.status_code == 404

        # User A attempts to POST to User B's expense
        response_post = auth_client.post(f'/expenses/{expense_id_b}/edit', data={
            'amount': '1.0', 'category': 'Food', 'date': '2026-01-01', 'description': 'Hacked'
        })
        assert response_post.status_code == 404

    def test_edit_expense_non_existent(self, auth_client):
        """Navigating to a non-existent expense ID returns 404."""
        response = auth_client.get('/expenses/999999/edit')
        assert response.status_code == 404
