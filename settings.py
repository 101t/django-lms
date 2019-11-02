import sys
import os
import dj_database_url
from datetime import timedelta

from celery.schedules import crontab
import django.conf.global_settings as DEFAULT_SETTINGS

# Django settings for intranet project.

DEBUG = True #True if os.environ.get('DEBUG', False) == 'True' else False
TEMPLATE_DEBUG = DEBUG

## Directories
SETTINGS_DIRECTORY = os.path.dirname( os.path.abspath(__file__) )
PROJECT_ROOT = SETTINGS_DIRECTORY

# Has db and all that stuff in it, the non-tracked things
SITE_ROOT = os.path.dirname( PROJECT_ROOT )

sys.path.append(SITE_ROOT)
sys.path.append(PROJECT_ROOT + '/apps')
sys.path.append(PROJECT_ROOT + '/libs')

MEDIA_ROOT = SITE_ROOT + '/media'

# Nonrel flag
NONREL = False

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + "/templates",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "libs.context_processors.settings",
    "libs.context_processors.user_groups",
    "social_auth.context_processors.social_auth_by_name_backends",
    )

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',

    # Third party apps

    'tinymce',
    'libs',
    'compressor',
    'djcelery',
    'mptt',
    'recurrence',
    'social_auth',
    'django_statsd',
    'django_extensions',
        
    # Local apps
    
    'apps.springboard',
    'apps.lms_admin',
    'apps.lms_main',
    'apps.courses',
    'apps.profiles',
    'apps.alerts',

    # Admin comes last so our apps can override some templates
    'django.contrib.admin',

    'gunicorn',
    
    ]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.facebook.FacebookBackend',
)

SOCIAL_AUTH_CREATE_USERS = False

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
)


STATIC_ROOT = SITE_ROOT + "/static"

STATIC_URL = "/static/"

STATICFILES_DIRS = (
    PROJECT_ROOT + "/static-files",
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + '/admin/'

LOGIN_REDIRECT_URL = '/'

#FIXME: This is a workaround with a bug in django-tinymce
import tinymce
TINYMCE_JS_URL = '%stiny_mce/tiny_mce.js' % STATIC_URL
STATICFILES_DIRS += (os.path.join(os.path.dirname(tinymce.__file__), 'media'),)

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'height': "400",
    'theme_advanced_buttons1' : "bold,italic,underline, strikethrough,link, separator,justifyleft, justifycenter,justifyright,  justifyfull, separator,help",
    'theme_advanced_buttons2': "",
    'theme_advanced_buttons3': "",
    'theme_advanced_buttons4': "",
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    }

ALERTS_FROM = os.environ.get('ALERTS_FROM', "donotreply@example.com")

DATABASES = {'default': dj_database_url.config(default='sqlite:///db.sqlite3')}#postgres://localhost:5432/django_lms

FACEBOOK_EXTENDED_PERMISSIONS = ['email']

BROKER_URL = os.environ.get('BROKEN_URL', "amqp://guest:guest@localhost:5672//")
BROKER_VHOST = os.environ.get('BROKER_VHOST', "/")

CELERY_ALWAYS_EAGER = True if os.environ.get('CELERY_ALWAYS_EAGER', False) == 'True' else False
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYBEAT_SCHEDULE = {'expire_course_visibility':
                       {
                           'task':'expire_course_visibility',
                           'schedule': crontab(hour=1, minute=0),
                       },
                       'disable_faculty':
                       {
                           'task':'disable_faculty',
                           'schedule': crontab(hour=1, minute=0),
                       },
                      }


SECRET_KEY = 'a!azm0(i29*scd8!ak4ma&&&han43^#!_ighpwyj82)!!0m=ci'#os.environ.get('SECRET_KEY')
TYPEKIT_URL = os.environ.get('TYPEKIT_URL')
SITE_ID = os.environ.get('SITE_ID')

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_API_SECRET = os.environ.get('FACEBOOK_API_SECRET')

STATSD_CLIENT = os.environ.get('STATSD_CLIENT', 'django_statsd.clients.null')

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
) + MIDDLEWARE_CLASSES

import djcelery
djcelery.setup_loader()
