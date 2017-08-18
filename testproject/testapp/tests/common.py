from django.contrib.auth import get_user_model
from django.db import IntegrityError

try:
    from unittest import mock
except ImportError:
    import mock

__all__ = ['get_user_model', 'IntegrityError', 'mock']


def create_user(**kwargs):
    data = {
        'username': 'john',
        'password': 'secret',
        'email': 'john@beatles.com',
    }
    data.update(kwargs)
    user = get_user_model().objects.create_user(**data)
    user.raw_password = data['password']
    return user


def perform_create_mock(x):
    raise IntegrityError
