import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_password_reset_with_trailing_slash():
    client = APIClient()
    response = client.post('/password/reset/', {'email': 'test@localhost'})

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db(transaction=False)
def test_valid_password_reset_without_trailing_slash():
    client = APIClient()
    response = client.post('/password/reset', {'email': 'test@localhost'})

    assert response.status_code == status.HTTP_204_NO_CONTENT
