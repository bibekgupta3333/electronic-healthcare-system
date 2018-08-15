from .common import *

ALLOWED_HOSTS.append('127.0.0.1')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'medidata',
        'USER': 'postgres',
        'PASSWORD': 'test',
        'HOST': 'localhost',
    }
}


MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')