import pytest
from testapp.factories import UserFactory, TokenFactory
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

User = get_user_model()


@pytest.fixture
def user(db):
    return UserFactory.create()


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user_url(user):
    return reverse("user-detail", kwargs={User._meta.pk.name: user.pk})


def test_get_return_user(authenticated_client, user, user_url):
    token = TokenFactory.create(user=user)
    authenticated_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response = authenticated_client.get(user_url)

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data.keys()) == set(
        [User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS
    )


def test_email_change_with_send_activation_email_false(
    djoser_settings, authenticated_client, user, user_url
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = False
    data = {"email": "ringo@beatles.com"}

    token = TokenFactory.create(user=user)
    authenticated_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response = authenticated_client.put(user_url, data=data)

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert data["email"] == user.email
    assert user.is_active


def test_email_change_with_send_activation_email_true(
    djoser_settings, authenticated_client, user, user_url, mailoutbox
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    data = {"email": "ringo@beatles.com"}

    token = TokenFactory.create(user=user)
    authenticated_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response = authenticated_client.put(user_url, data=data)

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert data["email"] == user.email
    assert not user.is_active
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [data["email"]]


def test_fail_403_without_permission(
    djoser_settings, authenticated_client, user, user_url
):
    djoser_settings["HIDE_USERS"] = False
    other_user = UserFactory.create(
        **{
            "username": "paul",
            "password": "verysecret",
            "email": "paul@beatles.com",
        }
    )
    data = {"email": "ringo@beatles.com"}
    url = reverse("user-detail", kwargs={User._meta.pk.name: other_user.pk})

    token = TokenFactory.create(user=user)
    authenticated_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response1 = authenticated_client.put(url, data=data)
    assert response1.status_code == status.HTTP_403_FORBIDDEN
    response2 = authenticated_client.get(user_url)
    assert response2.status_code == status.HTTP_200_OK


def test_fail_404_without_permission(
    djoser_settings, authenticated_client, user, user_url
):
    djoser_settings["HIDE_USERS"] = True
    other_user = UserFactory.create(
        **{
            "username": "paul",
            "password": "verysecret",
            "email": "paul@beatles.com",
        }
    )
    data = {"email": "ringo@beatles.com"}
    url = reverse("user-detail", kwargs={User._meta.pk.name: other_user.pk})

    token = TokenFactory.create(user=user)
    authenticated_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    response1 = authenticated_client.put(url, data=data)
    assert response1.status_code == status.HTTP_404_NOT_FOUND
    response2 = authenticated_client.get(user_url)
    assert response2.status_code == status.HTTP_200_OK
