from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from database.db import init_db, seed_db, get_db

app = Flask(__name__)
app.secret_key = 'dev-key-for-spendly'


# ------------------------------------------------------------------ #
# Helpers                                                                #
# ------------------------------------------------------------------ #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('profile'))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template("landing.html")

@app.context_processor
def inject_user():
    return dict(user_id=session.get('user_id'))


@app.route("/register", methods=["GET", "POST"])
@redirect_if_logged_in
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        hashed_password = generate_password_hash(password)

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hashed_password)
                )
                conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="This email is already registered.")
        except Exception as e:
            return render_template("register.html", error="An unexpected error occurred. Please try again.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@redirect_if_logged_in
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Email and password are required.")

        try:
            with get_db() as conn:
                user = conn.execute(
                    "SELECT id, password_hash FROM users WHERE email = ?",
                    (email,)
                ).fetchone()

                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    return redirect(url_for("profile"))
                else:
                    return render_template("login.html", error="Invalid email or password.")
        except Exception as e:
            return render_template("login.html", error="An unexpected error occurred. Please try again.")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    # Hardcoded data for Step 4 UI validation
    user_data = {
        "name": "Ganesh Anna",
        "email": "ganesh@example.com",
        "avatar_initials": "GA",
        "member_since": "January 2024"
    }

    stats = {
        "total_spent": "₹12,450.00",
        "transaction_count": 24,
        "top_category": "Food & Dining"
    }

    transactions = [
        {"date": "2024-09-18", "description": "Starbucks Coffee", "category": "Food & Dining", "amount": "₹350.00"},
        {"date": "2024-09-17", "description": "Uber Ride", "category": "Transport", "amount": "₹210.00"},
        {"date": "2024-09-15", "description": "Amazon - Keyboard", "category": "Electronics", "amount": "₹2,499.00"},
        {"date": "2024-09-12", "description": "Grocery Store", "category": "Groceries", "amount": "₹1,200.00"},
        {"date": "2024-09-10", "description": "Netflix Subscription", "category": "Entertainment", "amount": "₹499.00"},
    ]

    categories = [
        {"name": "Food & Dining", "amount": "₹4,200.00", "percentage": 34, "color": "var(--accent)"},
        {"name": "Transport", "amount": "₹2,100.00", "percentage": 17, "color": "var(--accent-2)"},
        {"name": "Electronics", "amount": "₹3,500.00", "percentage": 28, "color": "#5b7fa6"},
        {"name": "Entertainment", "amount": "₹1,500.00", "percentage": 12, "color": "#8b5e83"},
        {"name": "Others", "amount": "₹1,150.00", "percentage": 9, "color": "var(--ink-muted)"},
    ]

    return render_template(
        "profile.html",
        user=user_data,
        stats=stats,
        transactions=transactions,
        categories=categories
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
