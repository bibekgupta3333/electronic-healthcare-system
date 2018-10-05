import os
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured('Environment variable {name} not found.'.format(name=name))
