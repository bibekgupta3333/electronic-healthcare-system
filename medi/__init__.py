import os

if os.environ.get('DJANGO_SETTINGS_MODULE', None) == 'medi.settings.prod_settings':
    from medi.celery import app as celery_app

    __all__ = ['celery_app']
