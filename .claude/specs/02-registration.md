# Spec: Registration

## Overview
This feature implements the user registration process, allowing new users to create an account by providing their name, email, and password. This is a foundational step in the Spendly roadmap, enabling personalized expense tracking by establishing user identities.

## Depends on
- 01-database-setup

## Routes
- `GET /register` — Display registration form — public
- `POST /register` — Process registration and create user account — public

## Database changes
No database changes. The `users` table already exists with required columns (`name`, `email`, `password_hash`).

## Templates
- **Create:** None (using existing `register.html`)
- **Modify:** `templates/register.html` — Update to include a proper HTML form with `method="POST"` and necessary input fields.

## Files to change
- `app.py` — Implement the `POST /register` logic.
- `templates/register.html` — Implement the registration form.

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

## Definition of done
- [ ] Navigating to `/register` displays a form with Name, Email, and Password fields.
- [ ] Submitting the form with valid data creates a new user in the `users` table.
- [ ] Submitting the form with an existing email returns an appropriate error message.
- [ ] Passwords are stored as hashes in the database, not plain text.
- [ ] Successful registration redirects the user to the login page or dashboard.
