import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_user_me_with_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.get('/user/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        User.USERNAME_FIELD: 'test',
        User.get_email_field_name(): 'test@localhost',
        'id': 1,
    }


@pytest.mark.django_db(transaction=False)
def test_valid_user_me_without_trailing_slash(test_user):
    client = APIClient()
    client.force_login(test_user)
    response = client.get('/user')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        User.USERNAME_FIELD: 'test',
        User.get_email_field_name(): 'test@localhost',
        'id': 1,
    }
