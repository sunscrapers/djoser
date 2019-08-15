from django.contrib.auth import get_user_model
from django.db import IntegrityError

from djoser.conf import settings as djoser_settings

try:
    from unittest import mock
except ImportError:
    import mock

__all__ = [
    "get_user_model",
    "IntegrityError",
    "mock",
    "RunCheck",
    "PermCheckClass",
    "SerializerCheckClass",
]

Token = djoser_settings.TOKEN_MODEL


def create_user(use_custom_data=False, **kwargs):
    data = (
        {"username": "john", "password": "secret", "email": "john@beatles.com"}
        if not use_custom_data
        else {
            "custom_username": "john",
            "password": "secret",
            "custom_email": "john@beatles.com",
            "custom_required_field": "42",
        }
    )
    data.update(kwargs)
    user = get_user_model().objects.create_user(**data)
    user.raw_password = data["password"]
    return user


def login_user(client, user):
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


def perform_create_mock(x):
    raise IntegrityError


class RunCheck(Exception):
    pass


class PermCheckClass:
    def has_permission(self, *args, **kwargs):
        raise RunCheck("working")

    def has_object_permission(self, *args, **kwargs):
        raise RunCheck("working")


class SerializerCheckClass:
    def __init__(self, *args, **kwargs):
        raise RunCheck("working")
