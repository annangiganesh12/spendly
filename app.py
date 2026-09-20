from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import date
from database.queries import get_category_breakdown

from database.db import init_db, seed_db, get_db
from database.queries import get_summary_stats, get_user_by_id, get_recent_transactions

app = Flask(__name__)
app.secret_key = 'dev-key-for-spendly'

CATEGORIES = ['Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Other']


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

    # Capture date filters from request args
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Compute avatar initials from name
    name = user_data.get("name", "")
    initials = "".join([n[0].upper() for n in name.split() if n])[:2]
    user_data["avatar_initials"] = initials if initials else "U"

    stats = get_summary_stats(user_id, start_date, end_date)

    # Fetch real transaction history
    transactions = get_recent_transactions(user_id, start_date=start_date, end_date=end_date)

    categories = get_category_breakdown(user_id, start_date, end_date)

    return render_template(
        "profile.html",
        user=user_data,
        stats=stats,
        transactions=transactions,
        categories=categories,
        start_date=start_date,
        end_date=end_date
    )


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date_val = request.form.get("date")
        description = request.form.get("description")
        user_id = session.get("user_id")

        if not amount or not category or not date_val:
            return render_template("add_expense.html", error="Amount, category, and date are required.", categories=CATEGORIES, default_date=date.today().isoformat())

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return render_template("add_expense.html", error="Amount must be a positive number.", categories=CATEGORIES, default_date=date.today().isoformat())
        except ValueError:
            return render_template("add_expense.html", error="Invalid amount entered.", categories=CATEGORIES, default_date=date.today().isoformat())

        if category not in CATEGORIES:
            return render_template("add_expense.html", error="Invalid category selected.", categories=CATEGORIES, default_date=date.today().isoformat())

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                    (user_id, amount_float, category, date_val, description)
                )
                conn.commit()
            return redirect(url_for("profile"))
        except Exception as e:
            return render_template("add_expense.html", error="An error occurred while saving the expense. Please try again.", categories=CATEGORIES, default_date=date.today().isoformat())

    return render_template("add_expense.html", categories=CATEGORIES, default_date=date.today().isoformat())



@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    user_id = session.get("user_id")

    # Fetch the expense and verify ownership
    with get_db() as conn:
        expense = conn.execute(
            "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
            (id, user_id)
        ).fetchone()

    if not expense:
        abort(404)

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date_val = request.form.get("date")
        description = request.form.get("description")

        if not amount or not category or not date_val:
            return render_template("edit_expense.html", error="Amount, category, and date are required.", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return render_template("edit_expense.html", error="Amount must be a positive number.", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())
        except ValueError:
            return render_template("edit_expense.html", error="Invalid amount entered.", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())

        if category not in CATEGORIES:
            return render_template("edit_expense.html", error="Invalid category selected.", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())

        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ? AND user_id = ?",
                    (amount_float, category, date_val, description, id, user_id)
                )
                conn.commit()
            return redirect(url_for("profile"))
        except Exception as e:
            return render_template("edit_expense.html", error="An error occurred while updating the expense. Please try again.", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())

    return render_template("edit_expense.html", expense=expense, categories=CATEGORIES, default_date=date.today().isoformat())


@app.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    user_id = session.get("user_id")

    with get_db() as conn:
        # Ownership Verification
        expense = conn.execute(
            "SELECT id FROM expenses WHERE id = ? AND user_id = ?",
            (id, user_id)
        ).fetchone()

        if not expense:
            abort(404)

        # Parameterized Deletion
        conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (id, user_id)
        )
        conn.commit()

    return redirect(url_for("profile"))


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
