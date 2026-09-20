---
# Spec: Add Expense

## Overview
This feature allows logged-in users to record their spending by adding new expenses to their account. It provides a form where users can input the amount, category, date, and an optional description, enabling them to maintain an accurate record of their financial transactions.

## Depends on
- 03-login-logout (User must be authenticated)
- 05-backend-routes-for-profile-page (Basic database connection and user context)

## Routes
- `GET /expenses/add` — Render the "Add Expense" form — logged-in
- `POST /expenses/add` — Process the form submission and save the expense to the database — logged-in

## Database changes
No database changes. The `expenses` table already exists with columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, and `created_at`.

## Templates
- **Create:** `templates/add_expense.html`
- **Modify:** `templates/base.html` (Add a link to the "Add Expense" page in the navigation/profile)

## Files to change
- `app.py` (Implement the `add_expense` route and its POST handler)

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that `amount` is a positive number and `category` is provided.

## Definition of done
- [ ] Logged-in user can navigate to `/expenses/add` and see the form.
- [ ] Non-logged-in user is redirected to the login page when accessing `/expenses/add`.
- [ ] Submitting a valid expense successfully saves the record to the `expenses` table with the correct `user_id`.
- [ ] After successful submission, the user is redirected to the profile page.
- [ ] Form validation prevents submission of empty required fields or negative amounts.
- [ ] The new expense appears immediately in the transaction history on the profile page.
---
