import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_user_delete_with_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.delete(
        '/user/', {'current_password': 'testing123'}, format='json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.count() == 0


@pytest.mark.django_db(transaction=False)
def test_valid_user_delete_without_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.delete(
        '/user', {'current_password': 'testing123'}, format='json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.count() == 0