import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/{{ docs_version }}/howto/deployment/checklist/


# Application definition
INSTALLED_APPS = [
    "tests",
    "django_gov_notify",
]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "test-db.sqlite3"),
    }
}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "test-media")
MEDIA_URL = "http://media.example.com/media/"

SECRET_KEY = "not needed"  # pragma: allowlist secret

GOVUK_NOTIFY_API_KEY = "not a real API key"  # pragma: allowlist secret
GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID = str(uuid.uuid4())
