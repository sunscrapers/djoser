import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_user_update_with_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.put(
        '/user/', {'email': 'new-email@localhost'}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=False)
def test_valid_user_update_without_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.put(
        '/user/', {'email': 'new-email@localhost'}
    )

    assert response.status_code == status.HTTP_200_OK
