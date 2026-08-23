# dental-backend

API backend for the dental clinic CRM (patients & clinical records).

**Stack:** Python · Django · Django REST Framework · SimpleJWT · PostgreSQL (sqlite in dev).

> This repo is technical scaffolding only. Business apps (patients, appointments,
> clinical records, …) live under `apps/` and are not implemented yet.

## Requirements

- Python 3.11+ (developed on 3.13)
- PostgreSQL (optional; sqlite is used by default in dev)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env      # then edit values (Windows: copy .env.example .env)

# 4. Apply migrations
python manage.py migrate

# 5. Run the dev server
python manage.py runserver
```

The API is served at http://localhost:8000/ and the Django admin at
http://localhost:8000/admin/.

## Settings

Settings are split under `config/settings/`:

| Module                        | Use                                             |
| ----------------------------- | ----------------------------------------------- |
| `config.settings.base`        | Shared settings, reads from env via `django-environ`. |
| `config.settings.dev`         | Local development (default). Sensible defaults. |
| `config.settings.production`  | Production. Requires all env vars; HTTPS hardening. |

The active module is chosen with `DJANGO_SETTINGS_MODULE`:

- `manage.py` defaults to `config.settings.dev`
- `wsgi.py` / `asgi.py` default to `config.settings.production`

All configuration is read from environment variables — see `.env.example`.

## Project layout

```
dental-backend/
├── apps/               # Django business apps go here (empty for now)
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
└── .env.example
```

Apps placed under `apps/` are importable by their own name (e.g.
`INSTALLED_APPS += ["pacientes"]`) because `apps/` is added to the Python path
in `base.py`.

## What's already configured

- DRF with JWT (`rest_framework_simplejwt`) as the default authentication class.
- `IsAuthenticated` default permission and `PageNumberPagination` (page size 20).
- CORS allowing the frontend origin (`CORS_ALLOWED_ORIGINS`, default `http://localhost:3000`).
- Postgres-ready via `DATABASE_URL` (sqlite fallback in dev).

No business models, serializers, views, or JWT endpoints are wired up yet.
