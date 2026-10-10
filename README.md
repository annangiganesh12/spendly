# Spendly

**Track every rupee. Know where it goes.**

Spendly is a lightweight personal expense tracker built with **Flask** and **SQLite**. Users create an account, log their expenses in seconds, and get a dashboard that shows total spending, a category breakdown and recent transactions, with the option to filter everything by a date range.

The project was also built as a showcase of a professional **Claude Code workflow**: every feature starts from a written spec, and the repo includes custom slash commands, sub-agents, a skill, hooks and a `CLAUDE.md` guide. See [Built with Claude Code](#built-with-claude-code).

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Database Schema](#database-schema)
- [Routes](#routes)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Tests](#running-the-tests)
- [Built with Claude Code](#built-with-claude-code)
- [Scope for Improvement and Future Plan](#scope-for-improvement-and-future-plan)

---

## Features

| Area | What it does |
|---|---|
| **Accounts** | Register, log in and log out with session-based authentication and securely hashed passwords |
| **Add expenses** | Record an expense with amount, category, date and an optional description |
| **Edit and delete** | Update or remove any of your own expenses |
| **Dashboard** | A profile page with your avatar initials, member-since date, total spent, number of transactions and your top spending category |
| **Spending breakdown** | Per-category totals and percentages (adjusted so they always add up to exactly 100%) |
| **Recent transactions** | Your latest 10 transactions at a glance |
| **Date filter** | View the stats, breakdown and transactions for any start and end date |
| **Categories** | Food, Transport, Bills, Health, Entertainment, Shopping, Other |
| **Rupee formatting** | Amounts shown in the `₹1,234.50` format |
| **Landing page** | A public landing page, plus Terms and Privacy pages |

**Built-in safeguards**

- Passwords are stored as hashes, never as plain text.
- Every expense query is filtered by the logged-in user, so users cannot view, edit or delete each other's data. Trying to access someone else's expense returns a 404.
- All database queries are parameterized, which protects against SQL injection.
- Server-side validation: amount must be a positive number, the category must be in the allowed list, and required fields are checked.
- Logged-in users are redirected away from the login and register pages, and protected pages redirect to login.

---

## Tech Stack

- **Backend:** Python, Flask 3.1
- **Database:** SQLite (via Python's built-in `sqlite3`)
- **Security helpers:** Werkzeug password hashing
- **Frontend:** Jinja2 templates, custom CSS, vanilla JavaScript
- **Testing:** pytest, pytest-flask

---

## How It Works

1. A visitor lands on the home page and creates an account.
2. After logging in, they are taken to their dashboard (`/profile`).
3. They add expenses through a simple form; each expense is saved against their account.
4. The dashboard summarizes spending: totals, top category, a category breakdown and the latest transactions.
5. Setting a start and end date in the filter recalculates all of the dashboard numbers for that period.

---

## Database Schema

**users**

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key, auto-increment |
| `name` | TEXT | Required |
| `email` | TEXT | Required, unique |
| `password_hash` | TEXT | Required |
| `created_at` | TEXT | Defaults to the current timestamp |

**expenses**

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key, auto-increment |
| `user_id` | INTEGER | Foreign key to `users.id` |
| `amount` | REAL | Required |
| `category` | TEXT | Required |
| `date` | TEXT | Required (`YYYY-MM-DD`) |
| `description` | TEXT | Optional |
| `created_at` | TEXT | Defaults to the current timestamp |

Foreign keys are enforced on every connection.

---

## Routes

| Method | Route | Access | Description |
|---|---|---|---|
| GET | `/` | Public | Landing page (redirects to the dashboard if logged in) |
| GET, POST | `/register` | Public | Create an account |
| GET, POST | `/login` | Public | Log in |
| GET | `/logout` | Any | Clear the session |
| GET | `/profile` | Login required | Dashboard with stats, breakdown and recent transactions; supports `start_date` and `end_date` query parameters |
| GET, POST | `/expenses/add` | Login required | Add an expense |
| GET, POST | `/expenses/<id>/edit` | Login required | Edit one of your expenses |
| POST | `/expenses/<id>/delete` | Login required | Delete one of your expenses |
| GET | `/terms`, `/privacy` | Public | Legal pages |

---

## Project Structure

```
.
├── app.py                  # Flask app: configuration, auth, and all routes
├── setup_db.py             # One-off script to create and seed the database
├── database/
│   ├── db.py               # Connection helper, table creation, demo data seeding
│   └── queries.py          # Dashboard queries: stats, category breakdown, transactions
├── templates/              # Jinja2 pages (base layout, landing, auth, dashboard, expense forms)
├── static/
│   ├── css/                # Global and landing-page styles
│   └── js/main.js
├── tests/                  # pytest test suite
├── .claude/                # Claude Code workflow (see below)
│   ├── specs/              # 9 feature specs, one per step
│   ├── commands/           # custom slash commands
│   ├── agents/             # specialized sub-agents
│   ├── skills/             # UI design skill
│   └── settings.json       # hooks (auto-format, database protection)
├── requirements.txt
└── CLAUDE.md               # Project guidance for Claude Code
```

---

## Getting Started

### Prerequisites

- Python 3.10+

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/spendly.git
cd spendly
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the app

```bash
python app.py
```

On startup the app creates the SQLite database (`spendly.db`) and loads demo data. Open **http://localhost:5001**. To use a different port, set the `PORT` environment variable.

You can also initialize the database separately:

```bash
python setup_db.py
```

### 3. Try the demo account

| Field | Value |
|---|---|
| Email | `demo@spendly.com` |
| Password | `demo123` |

The demo user comes with sample expenses across all seven categories. Or create your own account on the register page.

---

## Running the Tests

```bash
pytest
```

The tests use an isolated in-memory database and cover the edit-expense flow (including ownership checks) and the profile page date filter.

---

## Built with Claude Code

Spendly was built feature by feature using a **spec-driven workflow with Claude Code**. The whole workflow lives in the repo, in `CLAUDE.md` and the `.claude/` folder, so anyone can see how each feature was planned, built, tested and reviewed.

### CLAUDE.md
Project guidance that Claude Code reads at the start of every session: common commands (install, run, test), the architecture, and where code belongs.

### Specs (`.claude/specs/`)
Each feature has a written spec before any code is written. A spec contains an overview, dependencies on earlier specs, the routes, database changes, templates and files to create or change, new dependencies, rules for implementation, and a **definition-of-done checklist**.

| # | Spec |
|---|------|
| 01 | Database setup |
| 02 | Registration |
| 03 | Login and logout |
| 04 | Profile page design |
| 05 | Backend routes for the profile page |
| 06 | Date filter for the profile page |
| 07 | Add expense |
| 08 | Edit expense |
| 09 | Delete expense |

Rules repeated in the specs keep the code consistent: parameterized queries only, no ORM, passwords hashed with Werkzeug, CSS variables instead of hard-coded colours, every template extends `base.html`, and every expense action checks that the expense belongs to the logged-in user.

### Custom slash commands (`.claude/commands/`)

| Command | What it does |
|---|---|
| `/create-spec` | Creates the spec file and a feature branch for the next step |
| `/test-feature` | Writes and runs tests for a feature, given its spec name |
| `/code-review-feature` | Runs security and quality reviews on the feature's changes in parallel |
| `/ship-feature` | Writes a conventional commit message, pushes, opens and merges the pull request, and cleans up the branch |
| `/seed-user` | Creates a realistic dummy user in the database |
| `/seed-expense` | Seeds realistic dummy expenses for a user over a number of months |

### Sub-agents (`.claude/agents/`)

| Agent | Role |
|---|---|
| `spendly-test-writer` | Writes pytest tests from the feature's spec and expected behaviour, not by reading the implementation |
| `spendly-test-runner` | Runs the tests and analyzes the results |
| `spendly-quality-reviewer` | Reviews the changed code for clean, maintainable Flask practices |
| `spendly-security-reviewer` | Reviews the changed code for common web security issues |

### Skill (`.claude/skills/`)
**`spendly-ui-designer`** guides how Claude designs the frontend: clean fintech-style pages and components built with Jinja2 templates and vanilla CSS, matching the project's stack and look.

### Hooks (`.claude/settings.json`)
- **Auto-format:** Python files are formatted with Black after every edit.
- **Safety guard:** shell commands that would delete or truncate protected files (`spendly.db`, `.env`, `migrations/`) are blocked.

### Typical feature loop
`/create-spec` → implement against the spec → `/test-feature` → `/code-review-feature` → `/ship-feature`

---

## Scope for Improvement and Future Plan

The app is a working foundation. The plan below describes how it can grow into a production-level product.

### Product features
- Monthly budgets with alerts when a category is close to its limit
- Charts and trends (spending over time, month-over-month comparison)
- Search, sorting and pagination of the full transaction history
- CSV export and import
- Recurring expenses, custom categories and multi-currency support
- Password reset and email verification

### Security and reliability
- Load the secret key from an environment variable instead of the source code
- Add CSRF protection to all forms and rate limiting on login and registration
- Add email format and password strength validation
- Secure cookie settings, HTTPS enforcement, and turning off debug mode in production
- Centralized error pages and structured logging

### Performance and scalability
- Move from SQLite to PostgreSQL with an ORM (SQLAlchemy) and migrations (Alembic)
- Connection pooling, database indexes on `user_id` and `date`, and query pagination
- Caching of dashboard summaries (Redis) for heavy users
- Serve the app with Gunicorn behind Nginx, with multiple workers and a load balancer for horizontal scaling

### DevOps
- **Docker:** containerize the app with a `Dockerfile` and a `docker-compose` setup including the database
- **CI/CD (GitHub Actions):** run linting and the pytest suite on every pull request, build and push the Docker image on merge, and deploy automatically to staging and production
- **Kubernetes:** deployment manifests with health probes, resource limits, autoscaling and an ingress with TLS
- Separate dev, staging and production configurations with secrets managed outside the repository

### Quality
- Expand test coverage to registration, login, add and delete flows, and the dashboard queries
- Add integration and end-to-end tests, and test coverage reporting in CI

---

## License

Add your preferred license here (for example MIT).
