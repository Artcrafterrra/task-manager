from .base import *

DEBUG = False

ALLOWED_HOSTS = [os.environ['RENDER_EXTERNAL_HOSTNAME']]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": int(os.environ["POSTGRES_DB_PORT"]),
    }
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": os.environ.get("CLIENT_ID", ""),
            "secret": os.environ.get("CLIENT_SECRET", ""),
            "key": "",
        },
    }
}
# SITE_ID = 1

