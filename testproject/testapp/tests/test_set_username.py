import pytest
from testapp.factories import TokenFactory
from testapp.factories import UserFactory, CustomUserFactory
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser
from unittest import mock

User = get_user_model()


@pytest.fixture
def base_url():
    return reverse(f"user-set-{User.USERNAME_FIELD}")


def test_post_set_new_username(api_client, base_url):
    user = UserFactory.create()
    data = {"new_username": "ringo", "current_password": "secret"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert data["new_username"] == user.username


def test_post_not_set_new_username_if_wrong_current_password(api_client, base_url):
    user = UserFactory.create()
    orig_username = user.get_username()
    data = {"new_username": "ringo", "current_password": "wrong"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert orig_username == user.username


def test_post_not_set_new_username_if_mismatch(djoser_settings, api_client, base_url):
    djoser_settings["SET_USERNAME_RETYPE"] = True
    user = UserFactory.create()
    data = {
        "new_username": "ringo",
        "re_new_username": "wrong",
        "current_password": "secret",
    }
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert data["new_username"] != user.username


def test_post_not_set_new_username_if_exists(api_client, base_url):
    username = "tom"
    UserFactory.create(username=username)
    user = UserFactory.create(username="john")
    data = {"new_username": username, "current_password": "secret"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert user.username != username


def test_post_not_set_new_username_if_invalid(api_client, base_url):
    user = UserFactory.create()
    data = {"new_username": "$ wrong username #", "current_password": "secret"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert user.username != data["new_username"]


def test_post_update_username_and_send_activation_email(
    djoser_settings, api_client, base_url, mailoutbox
):
    djoser_settings["USERNAME_CHANGED_EMAIL_CONFIRMATION"] = True
    user = UserFactory.create()
    data = {"new_username": "dango", "current_password": "secret"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]


def test_post_not_set_new_username_if_same(api_client, base_url):
    user = UserFactory.create()
    data = {"new_username": user.username, "current_password": "secret"}
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert user.is_active


@mock.patch("djoser.serializers.User", CustomUser)
@mock.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
@mock.patch(
    "djoser.serializers.SetUsernameSerializer.Meta.fields",
    (CustomUser.USERNAME_FIELD, "custom_username"),
)
@mock.patch("djoser.views.User", CustomUser)
@pytest.mark.django_db(transaction=True)
def test_post_set_new_custom_username(djoser_settings, api_client, base_url, settings):
    settings.AUTH_USER_MODEL = "testapp.CustomUser"
    djoser_settings["LOGIN_FIELD"] = CustomUser.USERNAME_FIELD
    user = CustomUserFactory.create(custom_required_field="42")
    data = {"new_custom_username": "ringo", "current_password": "secret"}
    api_client.force_authenticate(user)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert data["new_custom_username"] == user.get_username()


@mock.patch("djoser.serializers.User", CustomUser)
@mock.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
@mock.patch(
    "djoser.serializers.SetUsernameSerializer.Meta.fields",
    (CustomUser.USERNAME_FIELD, "custom_username"),
)
@mock.patch("djoser.views.User", CustomUser)
@pytest.mark.django_db(transaction=True)
def test_post_not_set_new_custom_username_if_mismatch(
    djoser_settings, api_client, base_url, settings
):
    settings.AUTH_USER_MODEL = "testapp.CustomUser"
    djoser_settings["SET_USERNAME_RETYPE"] = True
    djoser_settings["LOGIN_FIELD"] = CustomUser.USERNAME_FIELD
    user = CustomUserFactory.create(custom_required_field="42")
    data = {
        "new_custom_username": "ringo",
        "re_new_custom_username": "wrong",
        "current_password": "secret",
    }
    api_client.force_authenticate(user)

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert data["new_custom_username"] != user.get_username()
