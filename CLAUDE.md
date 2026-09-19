# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Application**: `python app.py` (Starts server on port 5001)
- **Run Tests**: `pytest`

## Architecture & Structure

- **Framework**: Flask (Python)
- **Application Entry**: `app.py` contains the application configuration and route definitions.
- **Database**: The `database/` directory is intended for database connection and schema management (e.g., `database/db.py`).
- **Frontend**:
    - **Templates**: Jinja2 HTML templates are located in `templates/`.
    - **Static Assets**: CSS and JavaScript files are located in `static/`.
- **Project State**: This is a boilerplate project where many routes and database functions are placeholders for implementation.
