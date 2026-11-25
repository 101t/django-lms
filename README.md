<div align="center">

# 🎓 Django LMS

**A lightweight, self-hosted Learning Management System you can install in one command.**

[![CI](https://github.com/101t/django-lms/actions/workflows/ci.yml/badge.svg)](https://github.com/101t/django-lms/actions/workflows/ci.yml)
[![Docker image](https://img.shields.io/badge/ghcr.io-101t%2Fdjango--lms-blue?logo=docker)](https://github.com/101t/django-lms/pkgs/container/django-lms)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue?logo=python)
![Django](https://img.shields.io/badge/django-5.2%20LTS-green?logo=django)

</div>

Most LMS platforms are heavy to run and hard to customise. Django LMS covers the everyday needs of a
school, department or bootcamp — courses, schedules, assignments, resources and announcements — in a
small, readable Django codebase that you can deploy on a $5 server.

## Features

- **Courses & semesters** — public or private courses, faculty, teaching assistants and students, self-enrolment for students.
- **Schedules & calendars** — recurring class meetings (iCal RRULEs), a semester calendar and a personal "my courses" calendar.
- **Assignments** — rich-text briefs, due dates, file or link submissions, team submissions and late flags.
- **Resources** — share files and links per course.
- **Alerts** — broadcast announcements to a user, groups or everyone, with optional email delivery in the background.
- **Dashboard** — a configurable app launcher, your courses and upcoming deadlines at a glance.
- **Profiles** — photo, résumé, biography, degrees and alumni status.
- **REST API** — read access to semesters, courses, assignments and resources plus alert management, documented with OpenAPI / Swagger at `/api/docs/`.
- **Automation** — scheduled jobs reset course visibility and deactivate idle faculty accounts at the end of each semester.
- **Modern UI** — Bootstrap 5 with dark mode, responsive on phones.
- **Production-ready** — PostgreSQL, Redis + Celery, Gunicorn, WhiteNoise and Caddy with automatic HTTPS, shipped as a multi-arch Docker image.

## Quick start

### One-line server install

On a fresh Linux server (Ubuntu, Debian, Fedora, …) with ports 80/443 open:

```bash
curl -fsSL https://raw.githubusercontent.com/101t/django-lms/master/install.sh | sudo DOMAIN=lms.example.edu bash
```

The installer sets up Docker if needed, generates secrets, starts the stack in `/opt/django-lms` and
prints the admin password. Point your domain's DNS at the server first and HTTPS is issued automatically.
Leave out `DOMAIN` to run over plain HTTP on the server's IP. Add `SEED_DEMO=1` to load demo courses and users.

To upgrade, run the same command again — your `.env` and data are kept.

### Docker Compose

```bash
git clone https://github.com/101t/django-lms.git && cd django-lms
cp example.env .env   # then set SECRET_KEY, POSTGRES_PASSWORD and ALLOWED_HOSTS; set DEBUG=false
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo   # optional demo data
```

Open <http://localhost>. Inside a git checkout, `docker-compose.override.yml` builds the image from source;
elsewhere the published image `ghcr.io/101t/django-lms` is used.

### Local development

Requires [uv](https://docs.astral.sh/uv/). No database or Redis needed — SQLite is the default and background tasks run inline.

```bash
git clone https://github.com/101t/django-lms.git && cd django-lms
echo "DEBUG=true" > .env
uv sync
uv run python manage.py migrate
uv run python manage.py seed_demo        # users: teacher / student1, password demo12345
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Run the checks before opening a pull request:

```bash
uv run python manage.py test
uv run ruff check . && uv run ruff format --check .
```

## Configuration

All settings come from environment variables (or `.env`). The most common ones:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEBUG` | `false` | Development mode. |
| `SECRET_KEY` | — | Required when `DEBUG` is off. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated host names. |
| `CSRF_TRUSTED_ORIGINS` | — | e.g. `https://lms.example.edu`. |
| `DATABASE_URL` | SQLite | e.g. `postgres://user:pass@host:5432/db`. |
| `REDIS_URL` | — | Enables the Celery worker; without it tasks run inline. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | — | SMTP. Emails are logged when unset. |
| `SITE_NAME` | `Django LMS` | Shown in the header and admin. |
| `TIME_ZONE` | `UTC` | |
| `SECURE_COOKIES` | `true` | Set `false` only when serving over plain HTTP. |

See [`example.env`](example.env) for the full list.

## How it fits together

| App | Responsibility |
| --- | --- |
| `apps/courses` | Semesters, courses, schedules, assignments, submissions, resources and calendars |
| `apps/alerts` | Announcements and email delivery |
| `apps/profiles` | User profiles, degrees and preferences |
| `apps/springboard` | The dashboard and its app tiles (configured in the admin) |
| `apps/api` | REST API and OpenAPI schema |
| `apps/lms_main` | Scheduled jobs and the `seed_demo` command |

Roles are Django groups: **Faculty**, **Students** and **Admissions** are created on first migration.
Put teachers in *Faculty* and learners in *Students*, then assign them to courses in the admin.

## API

Authenticate with your session or HTTP Basic auth, then browse the interactive docs at `/api/docs/`.

```bash
curl -u teacher:demo12345 https://lms.example.edu/api/v1/courses/?mine=1
```

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
