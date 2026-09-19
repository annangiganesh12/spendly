---
# Spec: Date Filter for Profile Page

## Overview
Currently, the profile page displays all transactions and statistics for the user regardless of the date. This feature introduces a date filter that allows users to filter their expenses and summary statistics by a specific time range (e.g., last 30 days, this month, custom range), providing more granular insights into their spending habits.

## Depends on
- 05-backend-routes-for-profile-page

## Routes
No new routes. The existing `/profile` route will be modified to handle optional date filter parameters (e.g., `start_date` and `end_date` query strings).

## Database changes
No database changes. The existing `expenses` table already contains a `date` column (TEXT) which will be used for filtering via SQL `WHERE` clauses.

## Templates
- **Modify:** `templates/profile.html` — Add a filter form (date inputs) to the UI and update the display to reflect the filtered state.

## Files to change
- `app.py` — Update the `profile` route to capture query parameters and pass them to database query functions.
- `database/queries.py` — Update `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` to accept optional date filters and apply them to the SQL queries.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Date filtering must be handled on the server side via SQL queries.
- Handle cases where date inputs might be empty or invalid gracefully.

## Definition of done
- [ ] User can select a start and end date on the profile page.
- [ ] Clicking "Filter" updates the "Total Spent" and "Recent Transactions" to only include items within that range.
- [ ] The "Category Breakdown" chart/list updates to reflect only the filtered expenses.
- [ ] Removing dates and filtering again restores the full view of all expenses.
- [ ] The app does not crash when providing invalid date formats.
---
