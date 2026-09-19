from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from database.queries import get_category_breakdown
from database.db import init_db, seed_db, get_db
from database.queries import get_summary_stats, get_user_by_id, get_recent_transactions

app = Flask(__name__)
app.secret_key = 'dev-key-for-spendly'


# ------------------------------------------------------------------ #
# Helpers                                                              #
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


@app.template_filter('format_currency')
def format_currency(value):
    try:
        if value is None:
            return "₹0.00"
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


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
    # Fetch real user data
    user_id = session['user_id']
    user_data = get_user_by_id(user_id)

    if not user_data:
        return redirect(url_for('logout'))

    # Compute avatar initials from name
    name = user_data.get("name", "")
    initials = "".join([n[0].upper() for n in name.split() if n])[:2]
    user_data["avatar_initials"] = initials if initials else "U"

    stats = get_summary_stats(user_id)

    # Fetch real transaction history
    transactions = get_recent_transactions(user_id)

    categories = get_category_breakdown(user_id)

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
