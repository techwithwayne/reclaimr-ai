from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-reclaimr")
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Apps (only what we need for local dev) ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "apps.core",
    "apps.accounts",
    "apps.contacts",
    "apps.leads",
    "apps.sequences",
    "apps.messaging",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database: local sqlite for dev/tests ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Password validation (defaults) ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N / TZ ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIMEZONE", "America/Chicago")
USE_I18N = True
USE_TZ = True

# --- Static/Media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "collected_static"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- DRF minimal ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

# --- Email: console backend for local ---
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Reclaimr <noreply@example.com>"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Reclaimr required host/origin safety block (appended) ---
try:
    ALLOWED_HOSTS  # type: ignore[name-defined]
except Exception:
    ALLOWED_HOSTS = []
if not isinstance(ALLOWED_HOSTS, (list, tuple)):
    ALLOWED_HOSTS = []
ALLOWED_HOSTS = list({*ALLOWED_HOSTS, "apps.techwithwayne.com", "techwithwayne.pythonanywhere.com"})

try:
    CSRF_TRUSTED_ORIGINS  # type: ignore[name-defined]
except Exception:
    CSRF_TRUSTED_ORIGINS = []
if not isinstance(CSRF_TRUSTED_ORIGINS, (list, tuple)):
    CSRF_TRUSTED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = list({*CSRF_TRUSTED_ORIGINS, "https://apps.techwithwayne.com", "https://techwithwayne.pythonanywhere.com"})
# --- end Reclaimr block ---
