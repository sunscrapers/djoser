from django.contrib.auth import get_user_model
from django.db import IntegrityError

try:
    from unittest import mock
except ImportError:
    import mock

__all__ = ['get_user_model', 'IntegrityError', 'mock']


def create_user(use_custom_data=False, **kwargs):
    data = {
        'username': 'john',
        'password': 'secret',
        'email': 'john@beatles.com',
    } if not use_custom_data else {
        'custom_username': 'john',
        'password': 'secret',
        'custom_email': 'john@beatles.com',
        'custom_required_field': '42',
    }
    data.update(kwargs)
    user = get_user_model().objects.create_user(**data)
    user.raw_password = data['password']
    return user


def perform_create_mock(x):
    raise IntegrityError
