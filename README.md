# dental-backend

API backend for the dental clinic CRM (patients & clinical records).

**Stack:** Python · Django · Django REST Framework · SimpleJWT · PostgreSQL (sqlite in dev).

The business apps under `apps/` are implemented:

- **users** — custom `User` with roles (ADMIN, MANAGER, ASSISTANT, MEDICO) and
  role-based access control (`shared/permissions.py`).
- **pacientes** — Cliente/Paciente, clinical history, odontogram, documents and
  personal antecedents.
- **citas** — appointments, doctors, services (with sub-services), schedules,
  attention records and agenda notes.
- **ventas** — sales/billing: sale, line items, discounts, extras, installments
  (cuotas) and payments with a validation flow.

Auth is JWT (`/api/auth/token/`, `/api/auth/token/refresh/`) with refresh
rotation + blacklist. See the tests in each app (`apps/*/tests.py`) for the
security and integrity rules that are enforced.

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
├── apps/               # Business apps: users, pacientes, citas, ventas
├── shared/             # Cross-app helpers: permissions, validators, pagination
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

Apps live under `apps/` and are referenced by their full path (e.g.
`apps.pacientes`); each `AppConfig` sets an explicit `label`.

## Configuration highlights

- DRF with JWT (`rest_framework_simplejwt`) as the default authentication class;
  refresh rotation + blacklist, 30-min access tokens.
- `IsAuthenticated` default permission (per-viewset role classes on top) and
  pagination (page size 20, `?page_size=` up to 500).
- Custom exception handler maps `ProtectedError` to a 400 with a readable message.
- CORS allowing the frontend origin (`CORS_ALLOWED_ORIGINS`, default `http://localhost:3000`).
- Postgres-ready via `DATABASE_URL` (sqlite fallback in dev).

## Tests

```bash
python manage.py test apps
```

Covers the RBAC and data-integrity rules (privilege escalation, double-booking,
read-only cuota state, payment validation, DNI format, protected deletes, …).
