import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_user_create_with_trailing_slash():
    client = APIClient()
    response = client.post('/users/', {
        User.USERNAME_FIELD: 'test@localhost',
        'password': 'testing123',
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {User.USERNAME_FIELD: 'test@localhost', 'id': 1}


@pytest.mark.django_db(transaction=False)
def test_valid_user_create_without_trailing_slash():
    client = APIClient()
    response = client.post('/users', {
        User.USERNAME_FIELD: 'test@localhost',
        'password': 'testing123',
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {User.USERNAME_FIELD: 'test@localhost', 'id': 1}
