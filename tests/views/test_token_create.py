import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_token_create_with_trailing_slash(test_user, settings):
    from djoser.conf import settings as djoser_settings

    settings.DJOSER = dict(
        settings.DJOSER,
        **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
    )
    token_model = djoser_settings.TOKEN_MODEL
    djoser_settings.SERIALIZERS['token'].Meta.model = token_model

    client = APIClient()
    response = client.post('/token/', {
        User.USERNAME_FIELD: 'test',
        'password': 'testing123',
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {'token': test_user.auth_token.key}


@pytest.mark.django_db(transaction=False)
def test_valid_token_create_without_trailing_slash(test_user, settings):
    from djoser.conf import settings as djoser_settings

    settings.DJOSER = dict(
        settings.DJOSER,
        **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
    )
    token_model = djoser_settings.TOKEN_MODEL
    djoser_settings.SERIALIZERS['token'].Meta.model = token_model

    client = APIClient()
    response = client.post('/token', {
        User.USERNAME_FIELD: 'test',
        'password': 'testing123',
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {'token': test_user.auth_token.key}
