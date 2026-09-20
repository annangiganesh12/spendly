---
# Spec: Delete Expense

## Overview
This feature allows users to remove unwanted or incorrect expense entries from their history. To prevent accidental deletions, the feature will implement a confirmation step (either via a confirmation page or a JavaScript dialog) before permanently removing the record from the database.

## Depends on
- 08-edit-expense

## Routes
- `POST /expenses/<int:id>/delete` — Delete a specific expense after ownership verification — logged-in

## Database changes
No database changes.

## Templates
- **Create:** No new templates.
- **Modify:** 
    - `templates/profile.html`: Add a "Delete" link/button next to the "Edit" link in the transaction table.

## Files to change
- `app.py`: Implement the delete route logic.
- `templates/profile.html`: Add the delete action to the UI.

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
- Ownership Verification: The route must verify that the expense belongs to the currently logged-in user before deletion.
- Method: Use `POST` for deletion to prevent CSRF/accidental deletions via `GET` requests.

## Definition of done
- [ ] An "Delete" action is visible for each transaction on the profile page.
- [ ] Clicking "Delete" triggers a confirmation prompt.
- [ ] Upon confirmation, the expense is permanently removed from the database.
- [ ] The user is redirected back to the profile page after deletion.
- [ ] Attempting to delete an expense that doesn't belong to the user results in a 404 or unauthorized error.
---
