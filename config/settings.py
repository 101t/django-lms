import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True  # os.environ.get('DEBUG', False)

INSTALLED_APPS = [
	'apps.devserver',  # noqa
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.admin',
	'django.contrib.messages',
	'django.contrib.admindocs',
	'django.contrib.staticfiles',

	# Third party apps
	# 'compressor',
	'django_celery_beat',
	'django_extensions',

	'formtools',
	'libs',
	'localflavor',
	'mptt',
	'recurrence',
	'tinymce',

	# Local apps
	'apps.alerts',
	'apps.courses',
	'apps.lms_admin',
	'apps.lms_main',
	'apps.profiles',
	'apps.springboard',
	'apps.django_statsd',
]

MIDDLEWARE = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',

	'django_statsd.middleware.GraphiteRequestTimingMiddleware',
	'django_statsd.middleware.GraphiteMiddleware',
)

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.template.context_processors.i18n',
				'django.template.context_processors.media',
				'django.template.context_processors.static',
				'django.template.context_processors.tz',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',

				"libs.context_processors.settings",
				"libs.context_processors.user_groups",
			],
		},
	},
]

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}

ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_private_key')

SITE_ID = os.environ.get('SITE_ID')

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	# other finders..
	# 'compressor.finders.CompressorFinder',
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

STATIC_URL = "/static/"

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static-files/'),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
)

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

import tinymce

TINYMCE_JS_URL = '%stiny_mce/tiny_mce.js' % STATIC_URL
STATICFILES_DIRS += (os.path.join(os.path.dirname(tinymce.__file__), 'media'),)

TINYMCE_DEFAULT_CONFIG = {
	'theme': "advanced",
	'height': "400",
	'theme_advanced_buttons1': "bold,italic,underline, strikethrough,link, separator,justifyleft, justifycenter,justifyright,  justifyfull, separator,help",
	'theme_advanced_buttons2': "",
	'theme_advanced_buttons3': "",
	'theme_advanced_buttons4': "",
	'theme_advanced_toolbar_location': "top",
	'theme_advanced_toolbar_align': "left",
}

ALERTS_FROM = os.environ.get('ALERTS_FROM', "donotreply@example.com")

FACEBOOK_EXTENDED_PERMISSIONS = ['email']

BROKER_URL = os.environ.get('BROKEN_URL', "amqp://guest:guest@localhost:5672//")
BROKER_VHOST = os.environ.get('BROKER_VHOST', "/")

CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER', False) == 'True'
CELERYBEAT_SCHEDULER = 'celery.schedulers.DatabaseScheduler'
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
	'expire_course_visibility': {
		'task': 'expire_course_visibility',
		'schedule': crontab(hour=1, minute=0),
	},
	'disable_faculty': {
		'task': 'disable_faculty',
		'schedule': crontab(hour=1, minute=0),
	},
}

TYPEKIT_URL = os.environ.get('TYPEKIT_URL')

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_API_SECRET = os.environ.get('FACEBOOK_API_SECRET')

STATSD_CLIENT = os.environ.get('STATSD_CLIENT', 'django_statsd.clients.null')
