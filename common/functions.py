import os
from zxcvbn import zxcvbn
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
        raise ImproperlyConfigured('Environment variable {env_name} not found.'.format(env_name=name))


def verify_password(password: str, first_name: str=None, last_name: str=None, email: str=None) -> dict:
    max_score = 3
    results = zxcvbn(password, user_inputs=[first_name, last_name, email])
    data = {
        'verified': True,
        'warning': None
    }
    if results.get('score',0) < max_score:
        data['verified'] = False
        data['warning'] = results.get('feedback').get('suggestions')
    return data

