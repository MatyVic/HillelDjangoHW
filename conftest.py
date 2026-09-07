import pytest


@pytest.fixture(autouse=True)
def disable_static_manifest(settings):

    # Для Django 4.2+
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
    # Для Django < 4.2 (про всяк випадок)
    settings.STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
