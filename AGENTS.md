# Oguz Academy — Agent Guide

## Stack
- **Backend:** Django 5.2.5 + Django REST Framework 3.15.2 + PostgreSQL (Docker Compose)
- **Frontend:** React 19 + TypeScript 6 + Vite 8 + Tailwind CSS 4 (SPA)
- **Auth:** JWT (SimpleJWT) — access 30dəq, refresh 7 gün + Session (admin)
- **3rd party:** django-jazzmin (admin), django-filter, django-cors-headers, django-ckeditor, Pillow
- **Linting:** oxlint (frontend only)
- **No backend linter/formatter/CI configured**

## Setup
```bash
# Backend
pip install -r requirements.txt
docker compose up -d        # PostgreSQL (5432) + Adminer (8080)
python manage.py migrate
python manage.py runserver   # Django on :8000

# Frontend
cd frontend
npm install
npm run dev                  # Vite on :3000 (proxies /api → :8000)
```
- DB credentials: `oguz` / `admin` / `12345`
- `pgdb/` is a Docker volume mount — do not edit manually.
- `.env` not used; secrets are in `oguz/settings.py` (dev-only).
- Frontend proxies `/api` requests to `http://127.0.0.1:8000` via Vite dev server.

## Architecture
- **Backend** serves REST API at `/api/v1/` — JSON only, no server-rendered pages
- **Frontend** is a separate React SPA (`frontend/`) with client-side routing
- Django templates still exist in `account/`, `core/`, `courses/` but the SPA is the primary UI
- Admin panel at `/admin/` (Django + Jazzmin theme)

## Auth
- Custom `account.User` model with **`USERNAME_FIELD = 'email'`**
- `AUTH_USER_MODEL = 'account.User'` — import via `settings.AUTH_USER_MODEL` or `get_user_model()`
- JWT endpoints: `/api/v1/auth/login/`, `/api/v1/auth/refresh/`, `/api/v1/auth/verify/`
- Frontend stores tokens in `localStorage`, auto-redirects to `/login` on 401
- Admin panel uses Django session auth (separate from JWT)

## Django Apps (18 total)
| App | Purpose | Has API | Has Templates |
|-----|---------|:-------:|:-------------:|
| `account/` | User model, auth, registration | Yes | Yes |
| `core/` | Home, about, contact, events, search | No | Yes |
| `courses/` | Course info, exams, Course/Group CRUD | Yes | Yes |
| `students/` | Student management (OneToOne → User) | Yes | Yes |
| `teachers/` | Teacher management (OneToOne → User) | Yes | Yes |
| `payments/` | Payment tracking per student | Yes | Yes |
| `attendance/` | Daily attendance per student/group | Yes | Yes |
| `branches/` | Branches, rooms | Yes | No |
| `employees/` | Employee management | Yes | No |
| `reports/` | Dashboard stats API | Yes | No |
| `schedule/` | Schedules, lessons | Yes | No |
| `system_settings/` | System settings CRUD | Yes | No |
| `finance/` | Expenses, income categories | No | No |
| `homework/` | Homework assignments | No | No |
| `notifications/` | Notifications | No | No |
| `files/` | File uploads | No | No |
| `audit/` | Activity logs | No | No |
| `roles/` | RBAC roles/permissions | Yes | No |

## API Structure
All REST endpoints at `/api/v1/`. Registered in `oguz/api_urls.py` via DRF router.
- Default auth: `JWTAuthentication` + `SessionAuthentication`
- Default permission: `IsAuthenticated`
- Pagination: `LimitOffsetPagination` (PAGE_SIZE=20)
- Filters: `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`

## Frontend Structure
```
frontend/src/
├── App.tsx              # Routes + auth guard
├── services/api.ts      # Axios instance, all API calls
├── hooks/useAuth.tsx    # Auth context + JWT management
├── components/layout/   # AppLayout (sidebar + navbar)
├── features/
│   ├── login/           # LoginPage
│   ├── dashboard/       # DashboardPage
│   ├── students/        # StudentListPage, StudentFormPage
│   ├── teachers/        # TeacherListPage
│   ├── courses/         # CourseCategoryListPage, CourseListPage, CourseFormPage
│   ├── groups/          # GroupListPage, GroupDetailPage
│   ├── employees/       # EmployeeListPage, EmployeeFormPage, PositionListPage
│   ├── exams/           # ExamListPage
│   ├── settings/        # SettingsPage
│   └── profile/         # ProfilePage
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── assets/              # Static assets
```

## Frontend Commands
```bash
cd frontend
npm run dev       # Start Vite dev server (port 3000)
npm run build     # TypeScript check + Vite build
npm run lint      # Run oxlint
npm run preview   # Preview production build
```

## Key Settings (oguz/settings.py)
- `DEBUG = True`, `ALLOWED_HOSTS = ['*']`
- `LANGUAGE_CODE = 'az'`, `TIME_ZONE = 'Asia/Baku'`
- `STATICFILES_DIRS = [BASE_DIR / "static"]`
- `MEDIA_ROOT = BASE_DIR / "media/"`
- `CORS_ALLOW_ALL_ORIGINS = True`
- JWT access lifetime: 8 hours, refresh: 30 days

## Testing
- **No test files exist** in any app
- To add: `python manage.py test <app>` using Django TestCase

## Static Assets
- Backend CSS: `static/css/style.css`, `static/css/responsive.css`
- Backend JS: `static/js/main.js`
- Backend images: `static/images/` (16 PNGs)
- Frontend: Tailwind CSS 4 + custom CSS in `frontend/src/index.css`

## Templates
- `core/templates/base.html` — main layout for Django-rendered pages
- `account/` templates are standalone (extend `base.html`)
- SPA pages in `frontend/src/features/` override Django templates

## Admin
- Django admin at `/admin/` with Jazzmin theme
- Register models in each app's `admin.py`

## Git
- Remote: `https://github.com/teymurov-git/oguz_academy.git`
- Default branch: `main`
- No custom hooks or branch protection

## Common Pitfalls
- **Two auth systems:** JWT for SPA, session for admin panel — don't mix them
- **Django templates still exist** alongside the SPA — some pages may render both
- **`pgdb/` is a Docker volume** — never edit files inside it directly
- **Frontend must be built separately** — `npm run build` outputs to `frontend/dist/`
- **CORS is fully open** (`CORS_ALLOW_ALL_ORIGINS = True`) — dev only, tighten for production
- **No test coverage** — any change could break existing functionality silently
