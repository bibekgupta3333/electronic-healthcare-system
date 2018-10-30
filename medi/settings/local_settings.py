from .common import *

ALLOWED_HOSTS.append('localhost')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'medidata',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
    }
}

EMIS_API_HOST = 'http://medi2data.net:9443'
