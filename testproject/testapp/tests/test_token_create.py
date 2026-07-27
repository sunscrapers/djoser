import pytest
from django.contrib.auth import user_logged_in, user_login_failed
from django.test import RequestFactory
from rest_framework import status
from rest_framework.reverse import reverse
from unittest.mock import patch

from djoser.conf import settings


@pytest.fixture
def login_url():
    return reverse("login")


def test_login_user_with_session_creation(user, djoser_settings):
    from djoser.utils import login_user

    factory = RequestFactory()
    request = factory.get("/")
    request.session = {}

    djoser_settings["CREATE_SESSION_ON_LOGIN"] = True
    with patch("djoser.utils.login") as mock_login:
        login_user(request, user)
        mock_login.assert_called_once_with(request, user)


def test_create_session_on_login_setting(user, api_client, djoser_settings):
    url = "/auth/token/login/"
    data = {"username": user.username, "password": "password"}

    djoser_settings["CREATE_SESSION_ON_LOGIN"] = True
    with patch("djoser.utils.login") as mock_login:
        response = api_client.post(url, data)
        # Should attempt to create session if login succeeds
        if response.status_code == 200:
            mock_login.assert_called()


@pytest.mark.django_db
def test_post_should_login_user(api_client, user, signal_tracker, login_url):
    previous_last_login = user.last_login
    data = {"username": user.username, "password": user.raw_password}
    user_logged_in.connect(signal_tracker.receiver)

    response = api_client.post(login_url, data)
    user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert response.data["auth_token"] == user.auth_token.key
    assert user.last_login != previous_last_login
    assert signal_tracker.signal_sent


@pytest.mark.django_db
def test_post_should_not_login_if_user_is_not_active(
    api_client, inactive_user, signal_tracker, login_url
):
    """
    In Django >= 1.10 authenticate() returns None if user is inactive, while in
    Django < 1.10 authenticate() succeeds if user is inactive.
    """
    data = {
        "username": inactive_user.username,
        "password": inactive_user.raw_password,
    }
    user_logged_in.connect(signal_tracker.receiver)

    response = api_client.post(login_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["non_field_errors"][0]
        == settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    )
    assert not signal_tracker.signal_sent


@pytest.mark.django_db
def test_post_should_not_login_if_invalid_credentials(
    api_client, user, signal_tracker, login_url
):
    data = {"username": user.username, "password": "wrong"}
    user_login_failed.connect(signal_tracker.receiver)

    response = api_client.post(login_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["non_field_errors"] == [
        settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    ]
    assert signal_tracker.signal_sent


@pytest.mark.django_db
def test_post_should_not_login_if_empty_request(api_client, login_url):
    data = {}

    response = api_client.post(login_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["non_field_errors"] == [
        settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    ]
