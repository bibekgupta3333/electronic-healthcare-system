"""
Django settings for medi project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

from common.functions import get_env_variable

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.abspath(os.path.join(BASE_DIR, '../config/'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@rdh!%o$i9!8c%m5v1!sj(kv52z-23!cqw^o+qs@cybna81r%%'
AES_KEY = get_env_variable('AES_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # third party
    'import_export',
    'django_tables2',
    'django_filters',
    'bootstrap4',
    'raven.contrib.django.raven_compat',
    'django_extensions',
    'django_select2',
    'django_crontab',
    'django_clamd',
    'axes',
    'django_celery_results',
    #'silk',

    # app
    'accounts',
    'organisations',
    'services',
    'instructions',
    'medicalreport',
    'snomedct',
    'template',
    'onboarding',
    'permissions',
    'payment',
    'report',
    'library',
]

MIDDLEWARE = [
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'medi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'medi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

#django-axes Authentication backend
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

#django-axes CACHES
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    },
    'axes_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
AXES_CACHE = 'axes_cache'
AXES_FAILURE_LIMIT = 8 #The number of login attempts allowed before a record is created for the failed logins
#AXES_LOCKOUT_TEMPLATE = 'registration/locked_out.html'
#AXES_LOCKOUT_URL = '/locked/'
AXES_RESET_ON_SUCCESS = True

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = 'static'
STATIC_URL = '/static/'

EMIS_API_HOST = 'http://medi2data.net:9443'
PREFIX_EMIS_USER = 'emr'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

RAVEN_CONFIG = {
    'dsn': 'https://33c2417eac2f468dadf54d7061d533d2:e741c290968045c098a339001c99f49f@sentry.io/1267663',
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = "/media/"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_variable('SENDGRID_USER')
EMAIL_HOST_PASSWORD = get_env_variable('SENDGRID_PASS')
DEFAULT_FROM = 'MediData'


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/instruction/view-pipeline'
LOGOUT_REDIRECT_URL = '/accounts/login/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger'
}

DATE_INPUT_FORMATS = [
    '%d/%m/%Y',     # 25/10/2006
    '%d/%m/%y',     # 25/10/06
]

CRONJOBS = [
    ('0 8 * * *', 'instructions.cron.notification_mail.instruction_notification_email_job'),
    ('0 0 * * *', 'report.cron.notification_mail.report_notification_expired_authorisation_job'),
    ('0 11,16 * * *', 'instructions.cron.notification_mail.send_email_to_practice_job'),
    ('1 0 * * SUN', 'payment.cron.genarate_invoice.genarated_weekly_invoice'),
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# getaddress.io API KEY
GET_ADDRESS_API_KEY = '5iggrV83fEmZQtq-H0zEBQ15848'

# checkmobi API KEY
CHECKMOBI_SECRET_KEY = '4591B789-9143-42DD-B5CF-CBE99F9A262A'

# mdx dual consent form template
MDXCONSENT_DIR = os.path.join(BASE_DIR, 'templates/instructions/mdx_dual_consent.html')

#MEDI ref number
MEDI_REF_NUMBER = 10000000


SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 600 # 10 Minutes
SESSION_SAVE_EVERY_REQUEST = True

#Clam AV setting
CLAMD_SOCKET = '/var/run/clamav/clamd.ctl'
CLAMD_USE_TCP = False
CLAMD_TCP_SOCKET = 3310
CLAMD_TCP_ADDR = '127.0.0.1'

#Remove comment for disable virus scanning for development
#CLAMD_ENABLED = False

#Set false for disable two factor authentication
TWO_FACTOR_ENABLED = True

#Set false for disable celery
CELERY_ENABLED = True
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'django-db'

MDX_URL = 'https://mdx.medi2data.com'
EMR_URL = 'https://emr.medi2data.com'

SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_AUTHENTICATION = True

#Set default handle 403!
CSRF_FAILURE_VIEW = 'services.views.handler_403'

#Set false for disable celery
IMAGE_REDACTION_ENABLED = True

# Set False for disable send new instruction email to Medidata User
NEW_INSTRUCTION_SEND_MAIL_TO_MEDI = False

# Set False for disable site_control
SITE_CONTROL = True
