from .common import *

ALLOWED_HOSTS.append('medi.mohub.co')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'medi',
        'USER': 'medi',
        'PASSWORD': 'medi',
        'HOST': 'db',
        'PORT': '5432',
    }
}

