import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'spendly.db'

def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Creates the database tables."""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

def seed_db():
    """Inserts sample data for development."""
    with get_db() as conn:
        # Check if users already exist to prevent duplicate seeding
        user = conn.execute('SELECT id FROM users LIMIT 1').fetchone()
        if user:
            return

        # Insert Demo User
        cursor = conn.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            ('Demo User', 'demo@spendly.com', generate_password_hash('demo123'))
        )
        demo_user_id = cursor.lastrowid

        # Sample expenses covering all categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        sample_expenses = [
            (demo_user_id, 12.50, 'Food', '2026-09-01', 'Lunch at Cafe'),
            (demo_user_id, 45.00, 'Transport', '2026-09-02', 'Weekly Fuel'),
            (demo_user_id, 120.00, 'Bills', '2026-09-03', 'Internet Bill'),
            (demo_user_id, 30.00, 'Health', '2026-09-05', 'Pharmacy'),
            (demo_user_id, 15.00, 'Entertainment', '2026-09-07', 'Movie Ticket'),
            (demo_user_id, 89.99, 'Shopping', '2026-09-10', 'New T-shirt'),
            (demo_user_id, 10.00, 'Other', '2026-09-12', 'Miscellaneous'),
            (demo_user_id, 22.00, 'Food', '2026-09-15', 'Dinner'),
        ]

        conn.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            sample_expenses
        )
        conn.commit()
