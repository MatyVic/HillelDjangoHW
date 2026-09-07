"""
WSGI config for bookstoreHW project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Default to development; production sets DJANGO_SETTINGS_MODULE explicitly
# as a real platform env var (Railway/Render/Heroku), which setdefault()
# will not override.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookstoreHW.settings.development")

application = get_wsgi_application()
