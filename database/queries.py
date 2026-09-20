import sqlite3
from datetime import datetime
from database.db import get_db

def get_user_by_id(user_id):
    """Fetches user profile info and formats the member since date."""
    with get_db() as conn:
        user = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            return None

        # Format created_at (YYYY-MM-DD HH:MM:SS) to "Month YYYY"
        try:
            dt = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
            member_since = dt.strftime('%B %Y')
        except (ValueError, TypeError):
            member_since = "Unknown"

        return {
            "name": user['name'],
            "email": user['email'],
            "member_since": member_since
        }

def get_summary_stats(user_id, start_date=None, end_date=None):
    """Calculates total spent, transaction count, and top category for a user."""
    with get_db() as conn:
        # Build query dynamically to avoid issues with SQLite NULL comparisons in some versions
        query_totals = "SELECT SUM(amount) as total, COUNT(id) as count FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query_totals += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query_totals += " AND date <= ?"
            params.append(end_date)

        totals = conn.execute(query_totals, params).fetchone()

        query_top_cat = "SELECT category FROM expenses WHERE user_id = ?"
        params_cat = [user_id]
        if start_date:
            query_top_cat += " AND date >= ?"
            params_cat.append(start_date)
        if end_date:
            query_top_cat += " AND date <= ?"
            params_cat.append(end_date)
        query_top_cat += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"

        top_cat_row = conn.execute(query_top_cat, params_cat).fetchone()

        total_spent = totals['total'] if totals and totals['total'] is not None else 0
        transaction_count = totals['count'] if totals else 0
        top_category = top_cat_row['category'] if top_cat_row else "N/A"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }


def get_category_breakdown(user_id, start_date=None, end_date=None):
    """
    Calculates the spend breakdown by category for a user.
    Ensures percentages sum to exactly 100.
    """
    category_colors = {
        "Food": "var(--accent)",
        "Transport": "var(--accent-2)",
        "Bills": "#5b7fa6",
        "Health": "#8b5e83",
        "Entertainment": "#a65b8f",
        "Shopping": "#5ba68f",
        "Other": "var(--ink-muted)"
    }
    default_color = "var(--ink-muted)"

    with get_db() as conn:
        # Get total spend first for percentage calculation
        query_total = "SELECT SUM(amount) FROM expenses WHERE user_id = ?"
        params_total = [user_id]
        if start_date:
            query_total += " AND date >= ?"
            params_total.append(start_date)
        if end_date:
            query_total += " AND date <= ?"
            params_total.append(end_date)

        total_row = conn.execute(query_total, params_total).fetchone()
        total = total_row[0] if total_row and total_row[0] else 0

        if total == 0:
            return []

        # Get breakdown by category
        query_breakdown = "SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ?"
        params_breakdown = [user_id]
        if start_date:
            query_breakdown += " AND date >= ?"
            params_breakdown.append(start_date)
        if end_date:
            query_breakdown += " AND date <= ?"
            params_breakdown.append(end_date)
        query_breakdown += " GROUP BY category ORDER BY amount DESC"

        rows = conn.execute(query_breakdown, params_breakdown).fetchall()

        results = []
        total_pct = 0

        for row in rows:
            name = row['name']
            amount = row['amount']
            pct = round((amount / total) * 100)
            total_pct += pct

            results.append({
                "name": name,
                "amount": amount,
                "percentage": pct,
                "color": category_colors.get(name, default_color)
            })

        # Adjust the largest category to ensure sum is exactly 100
        diff = 100 - total_pct
        if diff != 0 and results:
            results[0]["percentage"] += diff

        return results

def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    """Fetches the most recent transactions for a user."""
    with get_db() as conn:
        query = "SELECT id, date, description, category, amount FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
