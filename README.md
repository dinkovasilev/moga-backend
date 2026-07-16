# MOGA Backend

Django-based backend application designed to support a mobile platform with features such as:

- User and player management
- Task system and filtering
- Messaging and notifications
- Modular architecture with multiple apps
- REST-style backend structure (Django + DRF)

## Tech Stack

- Python 3
- Django 5
- Django REST Framework
- Channels (WebSockets)
- SQLite (dev)
- Redis (required for chat/notifications, via Channels)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/dinkovasilev/moga-backend.git
cd moga-backend
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Copy `.env.example` to `.env` and set a real `SECRET_KEY`:

```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(50))"  # paste the output into .env
```

### 5. Run Redis (required for chat/notifications)

```bash
redis-server
```

### 6. Run migrations

```bash
python manage.py migrate
```

This also seeds a default set of task/item categories so the demo isn't empty.

### 7. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 8. Run server

```bash
python manage.py runserver
```

## Notes

- Project is under active development, primarily a personal hobby project
- Item management (`apps/item`) is a known work in progress
- Designed as a backend for a mobile application

## Author

Dinko Vasilev
