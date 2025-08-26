from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


SECRET_KEY = (
    "django-insecure-zn4*rfpnt65pt1)k&b16cll&&ufu8!*57zc4+@!t8(=y8wi)@="
)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tracker",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "cloudinary",
    "cloudinary_storage",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "it_tasks.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tracker.context_processors.sidebar",
            ],
        },
    },
]

WSGI_APPLICATION = "it_tasks.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "tracker.Worker"


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Kiev"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATICFILES_DIRS = (BASE_DIR / "static",)

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


MEDIA_URL = "/media/"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUD_API_KEY"),
    "API_SECRET": os.environ.get("CLOUD_API_SECRET"),
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL

LOGOUT_REDIRECT_URL = "/accounts/login/"

LOGIN_URL = "/accounts/login/"

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}


SOCIALACCOUNT_LOGIN_ON_GET = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
