"""
ASGI config for bookstoreHW project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Default to development; production sets DJANGO_SETTINGS_MODULE explicitly
# as a real platform env var (Railway/Render/Heroku), which setdefault()
# will not override.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookstoreHW.settings.development")

application = get_asgi_application()
