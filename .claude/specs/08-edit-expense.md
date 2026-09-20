---
# Spec: Edit Expense

## Overview
This feature allows users to modify existing expense entries. It provides a way to correct mistakes in amount, category, date, or description, ensuring the expense tracker remains accurate. It follows the "Add Expense" flow but populates the form with existing data for the selected expense.

## Depends on
- 07-add-expense

## Routes
- `GET /expenses/<int:id>/edit` — Display the edit form with current expense data — logged-in
- `POST /expenses/<int:id>/edit` — Process and save the updated expense data — logged-in

## Database changes
No database changes.

## Templates
- **Create:** `templates/edit_expense.html`
- **Modify:** No templates modified.

## Files to change
- `app.py`

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Verify that the expense being edited belongs to the currently logged-in user to prevent unauthorized edits.

## Definition of done
- [ ] Navigating to `/expenses/<id>/edit` for a valid expense shows a form pre-filled with that expense's data.
- [ ] Submitting the edit form successfully updates the expense in the database.
- [ ] After a successful update, the user is redirected back to the profile page.
- [ ] Attempting to edit an expense that doesn't exist or doesn't belong to the user results in a 404 or unauthorized error.
- [ ] Validation rules for amount (positive number), category (must be in `CATEGORIES`), and date are enforced, similar to the "Add Expense" feature.
---
