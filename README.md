# IT Tasks Tracker
A Django-based web application for tracking tasks with user authentication, Google OAuth integration, and media storage via Cloudinary. Optimized for serving static files in production with WhiteNoise.

## Demo
Deployed at https://task-manager-mpqv.onrender.com/

Test credentials:
- login: test_user
- password: Pass123456

Or just sign up via Google

## Features
- User authentication (username/password via Django Allauth)
- Google OAuth login
- Custom user model
- Cloudinary-backed media storage
- Production-ready static files with WhiteNoise
- Configurable via environment variables

## Tech Stack
- Python 3.13
- Django
- Django Allauth
- Cloudinary + cloudinary-storage
- WhiteNoise
- SQLite (default for local development)

## Prerequisites
- Python 3.13
- virtualenv
- A Google Cloud project with OAuth credentials (for Google login)
- A Cloudinary account (for media storage)

## Instruction for local development
1. Clone the repository
``` bash
# Bash
git clone <YOUR_REPO_URL>.git
cd <YOUR_REPO_DIR>
```
1. Create and activate a virtual environment
``` bash
# Bash
python -m venv .venv
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```
1. Install dependencies
``` bash
# Bash
pip install -r requirements.txt
```
1. Configure environment variables

Create a .env file in the project root based on .env.sample:
``` dotenv
# Google AUTH
CLIENT_ID=Google_AUTH_CLIENT_ID
CLIENT_SECRET=Google_AUTH_CLIENT_SECRET

# CLOUDINARY
CLOUD_NAME=CLOUDINARY_CLOUD_NAME
CLOUD_API_KEY=CLOUDINARY_CLOUD_API_KEY
CLOUD_API_SECRET=CLOUDINARY_CLOUD_API_SECRET
CLOUDINARY_URL=CLOUDINARY_CLOUDINARY_URL

# DB (optional if you switch from SQLite)
DATABASE_URL=DATABASE_URL
POSTGRES_DB=POSTGRES_DB
POSTGRES_DB_PORT=POSTGRES_DB_PORT
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
POSTGRES_HOST=POSTGRES_HOST

# Django
SECRET_KEY=YOUR_SECURE_SECRET_KEY
DJANGO_SETTINGS_MODULE=it_tasks.settings
```
Notes:
- SECRET_KEY must be set to a strong, unique value.
- By default, the app uses SQLite for local development.
- CLOUDINARY credentials are required for file uploads.
- Google OAuth credentials are required if you plan to enable Google login.

1. Apply database migrations
``` bash
# Bash
python manage.py migrate
```
1. Create a superuser
``` bash
# Bash
python manage.py createsuperuser
```
1. Run the development server
``` bash
# Bash
python manage.py runserver
```
App will be available at:
- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- Auth routes (Allauth): /accounts/login/, /accounts/signup/, etc.

## Authentication
- Local login via username/password is enabled.
- Google login is supported via Django Allauth.

### Google OAuth Setup
1. Go to Google Cloud Console and create OAuth 2.0 credentials (Web application).
2. Add authorized redirect URI:

- [http://127.0.0.1:8000/accounts/google/login/callback/](http://127.0.0.1:8000/accounts/google/login/callback/)
- [http://localhost:8000/accounts/google/login/callback/](http://localhost:8000/accounts/google/login/callback/)

1. Put the CLIENT_ID and CLIENT_SECRET into your .env file.

## Media and Static Files
- Media storage uses Cloudinary. Set CLOUD_NAME, CLOUD_API_KEY, CLOUD_API_SECRET, and CLOUDINARY_URL in your .env.
- Static files are served by WhiteNoise in production. Make sure to run:
``` bash
# Bash
python manage.py collectstatic
```
## Configuration
- Allowed hosts are limited to localhost by default. For production, add your domain(s) to ALLOWED_HOSTS and CSRF trusted origins as needed.
- Timezone is set to Europe/Kiev.

## Deployment Tips
- Ensure SECRET_KEY is set via environment variables.
- Configure ALLOWED_HOSTS and CSRF trusted origins for your domain.
- Run collectstatic before starting the app in production.
- Use a persistent database in production and set appropriate environment variables if you configure one.

## Common Management Commands
``` bash
# Bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py collectstatic
```
