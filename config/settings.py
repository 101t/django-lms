"""
Django-LMS settings. Everything deployment-specific comes from environment variables
(or a `.env` file in the project root). See `example.env` for the full list.
"""

import os
from pathlib import Path

import dj_database_url
from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
	return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
	return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


DEBUG = env_bool("DEBUG")

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
	if not DEBUG:
		raise ImproperlyConfigured("SECRET_KEY must be set when DEBUG is off.")
	SECRET_KEY = "insecure-dev-only-key"

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
# Container health checks call the app on localhost.
ALLOWED_HOSTS += [h for h in ("localhost", "127.0.0.1") if h not in ALLOWED_HOSTS]
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

SITE_NAME = os.environ.get("SITE_NAME", "Django LMS")

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"whitenoise.runserver_nostatic",
	"django.contrib.staticfiles",
	# Third party
	"django_celery_beat",
	"drf_spectacular",
	"recurrence",
	"rest_framework",
	"tinymce",
	# Local
	"libs",
	"apps.alerts",
	"apps.courses",
	"apps.lms_admin",
	"apps.lms_main",
	"apps.profiles",
	"apps.springboard",
	"apps.api",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"whitenoise.middleware.WhiteNoiseMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

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
				"libs.context_processors.site",
				"libs.context_processors.user_groups",
			],
		},
	},
]

DATABASES = {
	"default": dj_database_url.config(
		default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
		conn_max_age=600,
		conn_health_checks=True,
	)
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "login"

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
STORAGES = {
	"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
	"staticfiles": {
		# shortcut: no hashed filenames (works without collectstatic); switch to the Manifest variant for long-lived caching
		"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
	},
}
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Email: console backend in development, SMTP when EMAIL_HOST is set.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_BACKEND = (
	"django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")
ALERTS_FROM = os.environ.get("ALERTS_FROM", DEFAULT_FROM_EMAIL)

# Celery: without a broker, tasks run inline so the app works with zero extra services.
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "")
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
	"expire-course-visibility": {
		"task": "apps.lms_main.tasks.expire_course_visibility",
		"schedule": crontab(hour=1, minute=0),
	},
	"disable-faculty": {
		"task": "apps.lms_main.tasks.disable_faculty",
		"schedule": crontab(hour=1, minute=0),
	},
}

CAMPUSES = [("main", "Main")]

TINYMCE_DEFAULT_CONFIG = {
	"height": 360,
	"menubar": False,
	"plugins": "link lists autolink code table",
	"toolbar": "undo redo | blocks | bold italic underline | bullist numlist | link table | code",
	"promotion": False,
}

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": [
		"rest_framework.authentication.SessionAuthentication",
		"rest_framework.authentication.BasicAuthentication",
	],
	"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
	"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
	"PAGE_SIZE": 50,
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS = {
	"TITLE": "Django LMS API",
	"DESCRIPTION": "REST API for courses, assignments, resources and alerts.",
	"VERSION": "2.0.0",
}

if not DEBUG:
	SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
	SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
	SESSION_COOKIE_SECURE = env_bool("SECURE_COOKIES", True)
	CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
	SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"handlers": {"console": {"class": "logging.StreamHandler"}},
	"root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}
