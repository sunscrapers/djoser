import pytest
from testapp.factories import UserFactory
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings


@pytest.mark.django_db
def test_post_set_new_password(api_client, mailoutbox):
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert user.check_password(data["new_password"])
    assert len(mailoutbox) == 0


@pytest.mark.django_db
def test_post_not_set_new_password_if_broken_uid(api_client):
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": "x",
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "uid" in response.data
    user.refresh_from_db()
    assert not user.check_password(data["new_password"])


@pytest.mark.django_db
def test_post_readable_error_message_when_uid_is_broken(api_client):
    """Regression test for
    https://github.com/sunscrapers/djoser/issues/122.

    When uid was not correct unicode string, error message was a
    standard Python error messsage. Now we provide human readable
    message.
    """
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": b"\xd3\x10\xb4",
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "uid" in response.data
    assert len(response.data["uid"]) == 1
    assert (
        response.data["uid"][0] == default_settings.CONSTANTS.messages.INVALID_UID_ERROR
    )


@pytest.mark.django_db
def test_post_not_set_new_password_if_user_does_not_exist(api_client):
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk + 1),
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "uid" in response.data
    user.refresh_from_db()
    assert not user.check_password(data["new_password"])


@pytest.mark.django_db
def test_post_not_set_new_password_if_wrong_token(api_client):
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": "wrong-token",
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["token"] == [
        default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR
    ]
    user.refresh_from_db()
    assert not user.check_password(data["new_password"])


@pytest.mark.django_db
def test_post_not_set_new_password_if_password_mismatch(api_client, djoser_settings):
    djoser_settings.update(PASSWORD_RESET_CONFIRM_RETYPE=True)
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
        "re_new_password": "wrong",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["non_field_errors"] == [
        default_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    ]


@pytest.mark.django_db
def test_post_not_set_new_password_if_mismatch(api_client, djoser_settings):
    djoser_settings.update(PASSWORD_RESET_CONFIRM_RETYPE=True)
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
        "re_new_password": "wrong",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert not user.check_password(data["new_password"])


@pytest.mark.django_db
def test_post_not_reset_if_fails_password_validation(api_client, djoser_settings):
    djoser_settings.update(PASSWORD_RESET_CONFIRM_RETYPE=True)
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
        "new_password": "666",
        "re_new_password": "isokpassword",
    }

    response = api_client.post(base_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"new_password": ["Password 666 is not allowed."]}


@pytest.mark.django_db
def test_post_password_changed_confirmation_email(
    api_client, djoser_settings, mailoutbox
):
    djoser_settings.update(PASSWORD_CHANGED_EMAIL_CONFIRMATION=True)
    base_url = reverse("user-reset-password-confirm")
    user = UserFactory.create()
    data = {
        "uid": djoser.utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
        "new_password": "new password",
    }

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert user.check_password(data["new_password"])
    assert len(mailoutbox) == 1
    assert user.email in [recipient for email in mailoutbox for recipient in email.to]
