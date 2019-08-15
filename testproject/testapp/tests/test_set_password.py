from django.conf import settings
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from djoser.conf import settings as djoser_settings
from testapp.tests.common import create_user, login_user

Token = djoser_settings.TOKEN_MODEL


class SetPasswordViewTest(
    APITestCase, assertions.EmailAssertionsMixin, assertions.StatusCodeAssertionsMixin
):
    def setUp(self):
        self.base_url = reverse("user-set-password")

    def test_post_set_new_password(self):
        user = create_user()
        data = {"new_password": "new password", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertTrue(user.check_password(data["new_password"]))
        self.assert_emails_in_mailbox(0)

    def test_post_not_set_new_password_if_wrong_current_password(self):
        user = create_user()
        data = {"new_password": "new password", "current_password": "wrong"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_PASSWORD_RETYPE": True}))
    def test_post_not_set_new_password_if_mismatch(self):
        user = create_user()
        data = {
            "new_password": "new password",
            "re_new_password": "wrong",
            "current_password": "secret",
        }
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password(data["current_password"]))

    def test_post_not_set_new_password_if_fails_validation(self):
        user = create_user()
        data = {
            "new_password": "666",
            "re_new_password": "666",
            "current_password": "secret",
        }
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"new_password": ["Password 666 is not allowed."]}
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"LOGOUT_ON_PASSWORD_CHANGE": True})
    )
    def test_post_logout_after_password_change(self):
        user = create_user()
        data = {"new_password": "new password", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = Token.objects.filter(user=user).exists()
        self.assertFalse(is_logged)

    def test_post_not_logout_after_password_change_if_setting_is_false(self):
        user = create_user()
        data = {"new_password": "new password", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = Token.objects.filter(user=user).exists()
        self.assertTrue(is_logged)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_password_changed_confirmation_email(self):
        user = create_user()
        data = {"new_password": "new password", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertTrue(user.check_password(data["new_password"]))
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
