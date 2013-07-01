import os.path
from os import environ

###############################
# production settings on heroku
###############################
if environ.has_key('DATABASE_URL'):
    DEBUG = True

    # Parse database configuration from $DATABASE_URL
    import dj_database_url
    DATABASES = {
        'default':  dj_database_url.config(default='postgres://watttime@localhost/windfriendly')
        }

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

###############################
# common settings 
###############################

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'watttime.app@gmail.com'
EMAIL_HOST_PASSWORD = '233fwef43'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DEPLOY_PATH = os.path.dirname(os.path.realpath(__file__)) #.replace('\\','/'),

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [ 'watttime.herokuapp.com',
                  'watttime.com',
                  'localhost' ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DEPLOY_PATH, 'templates'),    
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'windfriendly',
    'accounts',
    'pages',
    'workers',
    'sms_tools',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.bitly',
#    'allauth.socialaccount.providers.dropbox',
    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.github',
#    'allauth.socialaccount.providers.google',
#    'allauth.socialaccount.providers.linkedin',
#    'allauth.socialaccount.providers.openid',
#    'allauth.socialaccount.providers.persona',
#    'allauth.socialaccount.providers.soundcloud',
#    'allauth.socialaccount.providers.stackexchange',
#    'allauth.socialaccount.providers.twitch',
#    'allauth.socialaccount.providers.twitter',
#    'allauth.socialaccount.providers.vimeo',
#    'allauth.socialaccount.providers.weibo',
    'south',
    'invitation',
    'registration',
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
        }
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

# twilio account info
TWILIO_ACCOUNT_SID = 'AC47b7cc2bf4f9d4bddf4b9d8ceaec8ab2'
TWILIO_AUTH_TOKEN = 'aeb4e02df008a4e4e1cf31828fb43c84'
WATTTIME_PHONE = '+16175534837'

# for django-allauth
AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
    "invitation.context_processors.remaining_invitations",
)

ACCOUNT_AUTHENTICATION_METHOD = ("username_email")
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
          'AUTH_PARAMS': { 'auth_type': 'reauthenticate' },
          'METHOD': 'js_sdk' #'oauth2' 
    },
    'google': {
        'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile'],
         'AUTH_PARAMS': { 'access_type': 'online' }
    }
}

# for django-invitation https://github.com/arctelix/django-invitation
INVITATION_USE_ALLAUTH = True
INVITE_MODE = True
ACCOUNT_INVITATION_DAYS = 14
INVITATIONS_PER_USER = 20
SOCIALACCOUNT_ADAPTER ="allauth.accountadapter.SocialAccountAdapter"
ACCOUNT_ADAPTER ="allauth.accountadapter.AccountAdapter"
ALLOW_NEW_REGISTRATIONS = True

# for facebook login
FACEBOOK_APP_ID='411609345605022'
FACEBOOK_API_SECRET='e1760826fbb9d58e2ab39d21c80293b3'

# for google login
GOOGLE_OAUTH2_CLIENT_ID = '838963675754'
GOOGLE_OAUTH2_CLIENT_SECRET = 'jRGCatPXaMDUROQVJ8hy6FZc'

