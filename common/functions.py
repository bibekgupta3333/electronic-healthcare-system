import os

from django.core.exceptions import ImproperlyConfigured


def multi_getattr(obj, attr, **kwargs):
    attributes = attr.split('.')
    for attribute in attributes:
        try:
            obj = getattr(obj, attribute)
        except AttributeError:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise
    return obj


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured('Environment variable {name} not found.'.format(name=name))