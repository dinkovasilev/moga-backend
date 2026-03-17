1. Description
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
- Redis (optional)

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd moga-backend-public/backend

2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Setup environment variables
Create a .env file based on .env.example

5. Run migrations
python manage.py migrate

6. Create superuser (optional)
python manage.py createsuperuser

7. Run server
python manage.py runserver

Notes
Project is under active development

Some components are still being refactored and extended

Designed as a backend for a mobile application

Author
Dinko Vasilev
