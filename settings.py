import os.path
import os
import sys
from datetime import timedelta
from djcelery import setup_loader
setup_loader()

environ_settings = [
        'EMAIL_HOST_PASSWORD',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'WATTTIME_PHONE',
        'FACEBOOK_APP_ID',
        'FACEBOOK_API_SECRET',
        'GOOGLE_OAUTH2_CLIENT_ID',
        'GOOGLE_OAUTH2_CLIENT_SECRET',
        'TWITTER_CA_CONSUMER_KEY',
        'TWITTER_CA_CONSUMER_SECRET',
        'TWITTER_CA_ACCESS_KEY',
        'TWITTER_CA_ACCESS_SECRET',
    ]

def copy_from_environ(keys):
    for key in keys:
        value = os.environ.get(key, None)
        if value is None:
            print ("Cannot find environment variable {}!".format(key))
        else:
            globals()[key] = value

copy_from_environ(environ_settings)

###############################
# production settings on heroku
###############################
if os.environ.has_key('DATABASE_URL'):
    DEBUG = False

    # Parse database configuration from $DATABASE_URL
    import dj_database_url
    DATABASES = {
        'default':  dj_database_url.config(default='postgres://watttime@localhost/windfriendly')
        }

    # celery with CloudAMPQ backend
    BROKER_URL = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost//')
    CELERY_RESULT_BACKEND = 'database'

###############################
# local development settings 
###############################
else:
    DEBUG = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'windfriendly.db',                      # Or path to database file if using sqlite3.
            'USER': 'watttime',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            }
        }
        
    # celery with Django backend
    BROKER_URL = 'django://'
    CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
    
###############################
# common settings 
###############################

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'watttime.app@gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# This allows one to call .get_profile() on a User object to retrieve the
# corresponding UserProfile object, if it exists.
AUTH_PROFILE_MODULE = 'accounts.UserProfile'


TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('WattTime Dev Team', 'dev@watttime.org'),
)
SEND_BROKEN_LINK_EMAILS = True
MANAGERS = ADMINS

DEPLOY_PATH = os.path.dirname(os.path.realpath(__file__)) #.replace('\\','/'),

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
# ".watttime.com" means all subdomains of watttime.com are okay. Alternatively
# we could permit only www.watttime.com, for example.
ALLOWED_HOSTS = [ 'watttime.herokuapp.com',
                  'watttime.com',
                  'watttime.org',
                  'watttime.net',
                  '.watttime.com',
                  '.watttime.org',
                  '.watttime.net',
                  'wattime.org',
                  '.wattime.org',
                  'localhost' ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = 'static'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(DEPLOY_PATH, 'collected_static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(DEPLOY_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u-83ak4v53rjt$43*+)*k4hvo9@gknks6mztx133omm879t!d)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DEPLOY_PATH, 'templates'),
)

INSTALLED_APPS = (
    'windfriendly',
    'accounts',
    'pages',
    'workers',
    'sms_tools',
    'watttime_shift',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'south',
    'corsheaders',
    'tastypie',
    'bootstrap3',
    'kombu.transport.django',
    'djcelery',
    # move django apps later 
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
        'console': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_URL = 'authenticate'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "pages.context_processors.google_analytics",
)

ACCOUNT_AUTHENTICATION_METHOD = ("username_email")


# google analytics 
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-42171038-1'
GOOGLE_ANALYTICS_DOMAIN = 'watttime.com'

# Cross-Origin Resource Sharing
CORS_ORIGIN_ALLOW_ALL = True

# tastypie settings
TASTYPIE_DATETIME_FORMATTING = 'iso-8601-strict'

# celery settings
BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_MAX_RETRIES = 0
CELERY_MESSAGE_COMPRESSION = 'gzip'
CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=30)
CELERY_CHORD_PROPAGATES = True
