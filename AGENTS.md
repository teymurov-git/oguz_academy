# Oguz Academy — Agent Guide

## Stack
- **Django 5.2.5** on Python 3.x, **PostgreSQL** via Docker Compose
- No frontend framework, no build step, no JS bundler
- **django-jazzmin** (admin theme, must be first in `INSTALLED_APPS`)
- **Pillow** for user photo uploads

## Setup
```bash
pip install -r requirements.txt
docker compose up -d        # starts PostgreSQL (port 5432) + Adminer (port 8080)
python manage.py migrate
python manage.py runserver
```
- DB credentials: `oguz` / `admin` / `12345`
- The `pgdb/` directory is a Docker volume mount — do not edit manually.
- `.env` not used; secrets are in `oguz/settings.py` (dev-only).

## Auth
- Custom `account.User` model with **`USERNAME_FIELD = 'email'`** (login uses email, not username)
- `AUTH_USER_MODEL = 'account.User'` — any new app referencing auth must import this model via `settings.AUTH_USER_MODEL` or `get_user_model()`
- Email activation flow exists (token-based) but activation send is **commented out** in `register` view
- Gmail SMTP (`oguz/settings.py:145-150`) configured but requires the app password to be valid

## Apps
| Directory | Purpose | Entrypoint |
|-----------|---------|------------|
| `account/` | Registration, login, profile, logout | `account/urls.py` |
| `core/` | Home, about, contact, events, search, dashboard | `core/urls.py` |
| `courses/` | Static course info pages, exams + registration, Course & Group CRUD | `courses/urls.py` |
| `students/` | Student management (linked to User via OneToOneField) | `students/urls.py` |
| `teachers/` | Teacher management (linked to User via OneToOneField) | `teachers/urls.py` |
| `payments/` | Payment tracking per student | `payments/urls.py` |
| `attendance/` | Daily attendance per student per group | `attendance/urls.py` |

URL prefixes: `/students/`, `/teachers/`, `/courses/`, `/groups/`, `/payments/`, `/attendance/`, `/dashboard/`, `/exams/`.  
Management pages require `user.is_staff`. All app URLs are included at root under `''` or their prefix.

## Key settings
- `DEBUG = True`, `ALLOWED_HOSTS = ['*']`
- `STATICFILES_DIRS = [BASE_DIR / "static"]` — static served directly in dev
- `MEDIA_ROOT = BASE_DIR / "media/"` — user photos stored at `media/user_photos/`
- `AUTH_PASSWORD_VALIDATORS` are all **enabled** (including minimum length)

## Testing
- **No test files exist** in any app. No test framework configured beyond Django's built-in `TestCase`.
- To add tests: `python manage.py test <app>` using standard Django TestCase.

## Linting / Formatting / CI
- **None configured.** No linter, formatter, pre-commit hooks, or CI workflows.
- `.gitignore` covers Python/Django defaults plus `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`.

## Static assets
- CSS: `static/css/style.css` (790 lines) + `static/css/responsive.css`
- JS: `static/js/main.js` — dropdowns, nav active state, mobile menu toggle
- Images: 16 PNGs in `static/images/`

## Templates
- All templates are per-app under `<app>/templates/`
- `core/templates/base.html` is the main layout (header, nav, footer)
- `courses/` templates each extend `base.html`; `account/` templates are standalone

## Admin
- Django admin at `/admin/`
- Jazzmin customizes the admin UI — add `ModelAdmin` registrations to admin.py as usual

## Git
- Remote: `https://github.com/teymurov-git/oguz_academy.git`
- Default branch: `main`
- No custom hooks, no branch protection rules active
