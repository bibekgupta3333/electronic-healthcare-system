import os

from celery import Celery

if os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE'))
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medi.settings.prod_settings')

app = Celery('medi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
