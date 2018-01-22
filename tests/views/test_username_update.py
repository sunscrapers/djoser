import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_username_update_with_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.post(
        '/user/{}/'.format(User.USERNAME_FIELD),
        {User.USERNAME_FIELD: 'test-new', 'current_password': 'testing123'}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db(transaction=False)
def test_valid_username_update_without_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.post(
        '/user/{}'.format(User.USERNAME_FIELD),
        {User.USERNAME_FIELD: 'test-new', 'current_password': 'testing123'}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
