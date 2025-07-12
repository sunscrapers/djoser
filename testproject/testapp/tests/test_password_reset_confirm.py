import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.fixture
def url():
    return reverse("user-reset-password-confirm")


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    def test_post_set_new_password(self, anonymous_api_client, user, url):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mail.outbox) == 0

    def test_post_not_set_new_password_if_broken_uid(
        self, anonymous_api_client, user, url
    ):
        original_password = "secret"
        token = default_token_generator.make_token(user)
        data = {
            "uid": "x",
            "token": token,
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        user.refresh_from_db()
        assert user.check_password(original_password)
        assert not user.check_password(data["new_password"])

    def test_post_readable_error_message_when_uid_is_broken(
        self, anonymous_api_client, user, url
    ):
        token = default_token_generator.make_token(user)
        data = {
            "uid": b"\xd3\x10\xb4",
            "token": token,
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        assert len(response.data["uid"]) == 1
        assert (
            response.data["uid"][0]
            == default_settings.CONSTANTS.messages.INVALID_UID_ERROR
        )

    def test_post_not_set_new_password_if_user_does_not_exist(
        self, anonymous_api_client, user, url
    ):
        original_password = "secret"
        uid = djoser.utils.encode_uid(user.pk + 1)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        user.refresh_from_db()
        assert user.check_password(original_password)
        assert not user.check_password(data["new_password"])

    def test_post_not_set_new_password_if_wrong_token(
        self, anonymous_api_client, user, url
    ):
        original_password = "secret"
        uid = djoser.utils.encode_uid(user.pk)
        data = {
            "uid": uid,
            "token": "wrong-token",
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["token"] == [
            default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR
        ]
        user.refresh_from_db()
        assert user.check_password(original_password)
        assert not user.check_password(data["new_password"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_password_if_password_mismatch(
        self, anonymous_api_client, user, url
    ):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "new password",
            "re_new_password": "wrong",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"] == [
            default_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
        ]

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_password_if_mismatch(
        self, anonymous_api_client, user, url
    ):
        original_password = "secret"
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "new password",
            "re_new_password": "wrong",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password(original_password)
        assert not user.check_password(data["new_password"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_reset_if_fails_password_validation(
        self, anonymous_api_client, user, url
    ):
        original_password = "secret"
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "666",
            "re_new_password": "666",
        }

        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        user.refresh_from_db()
        assert user.check_password(original_password)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_password_changed_confirmation_email(
        self, anonymous_api_client, user, url
    ):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_password": "new password",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
