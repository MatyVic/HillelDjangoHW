"""
Development settings - local `runserver` / local docker-compose work.

Activate with:
    DJANGO_SETTINGS_MODULE=bookstoreHW.settings.development

This is also the default baked into manage.py / wsgi.py / asgi.py, so plain
`python manage.py runserver` picks this up with no extra configuration.
"""

import os

from .base import *  # noqa: F401,F403
from .base import _load_env_file

# Keep supporting the existing .env_local file for local venv work.
# (docker-compose already injects .env_docker as real env vars via `env_file:`,
# so nothing extra is needed for the docker-compose flow.)
_load_env_file(".env_local")

DEBUG = True

# Fallback secret key so `runserver` works out of the box without a .env_local
# file. Never used in production - production.py requires DJANGO_SECRET_KEY
# to be set and raises if it's missing.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-4bn&sa=z2b##e#i=yep!8$pyq1hshbfc27j2bcg%i!fw-+a&mj",
)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:9000",
]

# Emails just print to the console - no real SMTP needed locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
