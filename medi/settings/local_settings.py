from .common import *

ALLOWED_HOSTS.append('127.0.0.1')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'medi_test',
        'USER': 'waltzhargen',
        'PASSWORD': '',
        'HOST': '',
    }
}

EMIS_API_HOST = 'http://medi.mohub.co:3001/emis'
