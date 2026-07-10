# Oguz Academy

Web application for **Oğuz Tədris Mərkəzi** (Oguz Educational Center) — an education center based in Baku, Azerbaijan.

## Tech Stack

- **Python 3.x**, **Django 5.2.5**
- **PostgreSQL** (via Docker Compose)
- **django-jazzmin** for admin UI theming
- **Pillow** for image uploads
- No frontend framework — plain HTML, CSS, JavaScript

## Features

- Course information pages (Python, Django, Informatics, Languages, etc.)
- User registration with email & profile photo upload
- Email-based authentication (login with email)
- Contact form with database storage
- Newsletter subscriber management
- Responsive design
- Django admin panel with Jazzmin theme

## Quick Start

### Prerequisites

- Python 3.x
- Docker & Docker Compose (for PostgreSQL)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start database
docker compose up -d

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

The app is available at `http://localhost:8000`.

## Routes

| Path | Description |
|------|-------------|
| `/` | Home page |
| `/about` | About the center |
| `/contact` | Contact form |
| `/events` | Event gallery |
| `/search` | Search |
| `/login/` | Login (email-based) |
| `/register/` | Register |
| `/profile/` | User profile |
| `/logout/` | Logout |
| `/admin/` | Django admin panel |
| `/python/`, `/django/`, `/informatics/`, etc. | Course pages |

## Project Structure

```
oguz_academy/
├── account/          # User auth (register, login, profile)
├── core/             # Main pages (home, about, contact, events)
├── courses/          # Course info pages
├── oguz/             # Django project settings & URL config
├── static/           # CSS, JS, images
│   ├── css/
│   ├── images/
│   └── js/
├── media/            # User-uploaded files
│   └── user_photos/
├── pgdb/             # PostgreSQL data (Docker volume)
├── docker-compose.yml
└── requirements.txt
```

## Admin

Access the admin panel at `/admin/`. Jazzmin provides a modern admin theme — register models in each app's `admin.py` as usual.
