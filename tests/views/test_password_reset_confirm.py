import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.test import APIClient

from djoser import utils

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_password_reset_confirm_with_trailing_slash(test_user):
    client = APIClient()
    response = client.post(
        '/password/reset/confirm/',
        {
            'uid': utils.encode_uid(test_user.pk),
            'token': default_token_generator.make_token(test_user),
            'new_password': 'cool-new-password123',
        }
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db(transaction=False)
def test_valid_password_reset_confirm_without_trailing_slash(test_user):
    client = APIClient()
    response = client.post(
        '/password/reset/confirm',
        {
            'uid': utils.encode_uid(test_user.pk),
            'token': default_token_generator.make_token(test_user),
            'new_password': 'cool-new-password123',
        }
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT