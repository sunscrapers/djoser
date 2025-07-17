import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail  # Import mail for email assertions
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.fixture
def url():
    # Use USERNAME_FIELD from the actual User model dynamically
    username_field = User.USERNAME_FIELD
    return reverse(f"user-reset-{username_field}-confirm")


@pytest.mark.django_db
class TestUsernameResetConfirmView:
    # Removed setUp and mixins

    def test_post_set_new_username(self, anonymous_api_client, user, url):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()

        assert user.username == data["new_username"]
        assert len(mail.outbox) == 0

    def test_post_not_set_new_username_if_broken_uid(
        self, anonymous_api_client, user, url
    ):
        original_username = user.username
        token = default_token_generator.make_token(user)
        data = {
            "uid": "x",
            "token": token,
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    def test_post_readable_error_message_when_uid_is_broken(
        self, anonymous_api_client, user, url
    ):
        token = default_token_generator.make_token(user)
        data = {
            "uid": b"\xd3\x10\xb4",  # Broken UID
            "token": token,
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        assert len(response.data["uid"]) == 1
        assert (
            response.data["uid"][0]
            == default_settings.CONSTANTS.messages.INVALID_UID_ERROR
        )

    def test_post_not_set_new_username_if_user_does_not_exist(
        self, anonymous_api_client, user, url
    ):
        original_username = user.username
        uid = djoser.utils.encode_uid(user.pk + 1)  # Non-existent PK
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data
        # The error message might vary, just check that uid is the field with error
        user.refresh_from_db()
        assert user.username == original_username

    def test_post_not_set_new_username_if_wrong_token(
        self, anonymous_api_client, user, url
    ):
        original_username = user.username
        uid = djoser.utils.encode_uid(user.pk)
        data = {
            "uid": uid,
            "token": "wrong-token",
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["token"] == [
            default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR
        ]
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_username_if_username_mismatch(
        self, anonymous_api_client, user, url
    ):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "new_username",
            "re_new_username": "wrong",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"] == [
            default_settings.CONSTANTS.messages.USERNAME_MISMATCH_ERROR.format(
                User.USERNAME_FIELD
            )
        ]

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_username_if_mismatch(
        self, anonymous_api_client, user, url
    ):
        # This test seems identical to test_post_not_set_new_username_if_username_mismatch # noqa: E501
        # Keeping it for consistency for now.
        original_username = user.username
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "new_username",
            "re_new_username": "wrong",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_reset_if_fails_username_validation(
        self, anonymous_api_client, user, url
    ):
        original_username = user.username
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "invalid username",  # Contains space, should fail validation  # noqa: E501
            "re_new_username": "invalid username",
        }

        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check that the error is related to the new_username field
        assert "new_username" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_username_changed_confirmation_email(
        self, anonymous_api_client, user, url
    ):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
            "new_username": "new_username",
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.username == data["new_username"]
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
