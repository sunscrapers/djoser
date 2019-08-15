from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings
from testapp.tests.common import create_user

User = get_user_model()


class UsernameResetConfirmViewTest(
    APITestCase, assertions.EmailAssertionsMixin, assertions.StatusCodeAssertionsMixin
):
    def setUp(self):
        self.base_url = reverse("user-reset-{}-confirm".format(User.USERNAME_FIELD))

    def test_post_set_new_username(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()

        self.assertEqual(data["new_username"], user.username)
        self.assert_emails_in_mailbox(0)

    def test_post_not_set_new_username_if_broken_uid(self):
        user = create_user()
        data = {
            "uid": "x",
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("uid", response.data)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    def test_post_readable_error_message_when_uid_is_broken(self):
        user = create_user()
        data = {
            "uid": b"\xd3\x10\xb4",
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("uid", response.data)
        self.assertEqual(len(response.data["uid"]), 1)
        self.assertEqual(
            response.data["uid"][0],
            default_settings.CONSTANTS.messages.INVALID_UID_ERROR,
        )

    def test_post_not_set_new_username_if_user_does_not_exist(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk + 1),
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("uid", response.data)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    def test_post_not_set_new_username_if_wrong_token(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": "wrong-token",
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["token"],
            [default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR],
        )
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_username_if_username_mismatch(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
            "re_new_username": "wrong",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"],
            [
                default_settings.CONSTANTS.messages.USERNAME_MISMATCH_ERROR.format(
                    User.USERNAME_FIELD
                )
            ],  # noqa
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_set_new_username_if_mismatch(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
            "re_new_username": "wrong",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_RESET_CONFIRM_RETYPE": True})
    )
    def test_post_not_reset_if_fails_username_validation(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
            "new_username": "new username",
            "re_new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_username_changed_confirmation_email(self):
        user = create_user()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
            "new_username": "new_username",
        }

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.username, data["new_username"])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
