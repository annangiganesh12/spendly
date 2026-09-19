# Spec: Login and Logout

## Overview
This feature implements the authentication flow, allowing registered users to sign into their accounts and securely sign out. This ensures that users can access their personal expense data and that sessions are managed correctly, providing a secure transition from a public visitor to a logged-in user. After logging in user should redirect to the landing page.

## Depends on
- 01-Database Setup
- 02-registration

## Routes
- `GET /login` — Display login form — public
- `POST /login` — Authenticate user and establish session — public
- `GET /logout` — Terminate user session — logged-in

## Database changes
No database changes.

## Templates
- **Create:** None
- **Modify:** `templates/login.html` — Update to include a proper HTML form with `method="POST"`.

## Files to change
- `app.py` — Implement the `POST /login` and `GET /logout` logic, including session management using Flask's `session` object.
- `templates/login.html` — Implement the login form.

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
- [ ] Navigating to `/login` displays a form with Email and Password fields.
- [ ] Submitting valid credentials successfully logs the user in and redirects to the profile or landing page.
- [ ] Submitting invalid credentials returns an error message on the login page.
- [ ] Logged-in users can access the `/logout` route, which clears the session and redirects to the landing page.
- [ ] Accessing a logged-in only route while signed out redirects the user to the login page.
