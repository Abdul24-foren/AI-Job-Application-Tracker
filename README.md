# CareerFlow — AI-Powered Job Application Tracker

A polished, local-first Flask application for organizing a job search. Track opportunities, manage application stages, set follow-up dates, export records, and compare resume text against a job description with a lightweight keyword analyzer.

> **Honest product note:** The resume matcher is an offline keyword-overlap helper, not a generative AI model, ATS simulator, or hiring prediction. No resume text is sent to an external service.

## Features

- Dashboard with pipeline metrics, status distribution, recent activity, and due follow-ups.
- Full application lifecycle: create, view, edit, update status, and delete.
- Search by company, role, or location; filter by status.
- Application details: location, job type, source, job URL, compensation, dates, recruiter contact, and notes.
- CSV export for backup or spreadsheet analysis.
- Resume/job-description keyword comparison with matched and missing terms.
- Responsive layout for desktop, tablet, and mobile.
- SQLite persistence; no separate database server required.
- Parameterized SQL queries and server-side validation.

## Requirements

- Python 3.10 or newer
- pip

## Quick start (Windows PowerShell)

```powershell
cd ai_job_application_tracker
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open http://127.0.0.1:5000 in your browser.

If PowerShell blocks virtual-environment activation, run the app using `.venv\Scripts\python.exe` directly after installing dependencies.

## Quick start (macOS / Linux)

```bash
cd ai_job_application_tracker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
```

Then open http://127.0.0.1:5000.

## Database and backups

The SQLite database is created automatically at `instance/tracker.sqlite3` on first run. The `instance/` directory is intentionally excluded from version control. Use **Export CSV** on the Applications page for a portable backup. Keep a copy of the database file as well if you want to preserve all records and metadata.

To use a different database location, set `DATABASE_PATH` in your environment.

## Configuration and deployment

Set a strong, unique `SECRET_KEY` before exposing the application beyond your own machine. The included development server is not intended for production deployment. For production, run behind a production WSGI server (for example, Waitress on Windows or Gunicorn on Linux) and HTTPS, restrict network access, and configure persistent storage and backups.

Example production server install:

```bash
pip install waitress
waitress-serve --host=127.0.0.1 --port=8000 run:app
```

This starter is designed as a **single-user local workspace**. It does not include account registration, multi-user authorization, cloud sync, or external AI integrations. Do not expose it publicly with private resume or contact data until authentication, authorization, CSRF protection, HTTPS, and deployment hardening have been added.

## Project structure

```text
ai_job_application_tracker/
├── app/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── db.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── applications.html
│   │   ├── application_form.html
│   │   ├── detail.html
│   │   └── resume_match.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   └── test_app.py
├── instance/              # created at runtime; local database
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Testing

Install dependencies, then run:

```bash
python -m unittest discover -s tests -v
```

## Suggested next upgrades

1. Add authentication and per-user data isolation.
2. Add CSRF protection and secure session configuration.
3. Add PDF resume upload and text extraction.
4. Add calendar reminders and email notifications.
5. Add optional LLM-powered resume feedback behind an explicit API configuration.
