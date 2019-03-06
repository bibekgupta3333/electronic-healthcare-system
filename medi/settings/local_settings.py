from .common import *

ALLOWED_HOSTS.append('localhost')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'medi',
        'USER': 'medi',
        'PASSWORD': 'medi',
        'HOST': '',
    }
}

EMIS_API_HOST = 'http://medi2data.net:9443'
TWO_FACTOR_ENABLED=False
CELERY_ENABLED=False
CLAMD_ENABLED= False
