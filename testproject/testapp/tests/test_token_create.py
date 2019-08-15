import django
from django.contrib.auth import user_logged_in, user_login_failed
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from djoser.conf import settings
from testapp.tests.common import create_user


class TokenCreateViewTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    def setUp(self):
        self.signal_sent = False
        self.base_url = reverse("login")

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_login_user(self):
        user = create_user()
        previous_last_login = user.last_login
        data = {"username": user.username, "password": user.raw_password}
        user_logged_in.connect(self.signal_receiver)

        response = self.client.post(self.base_url, data)
        user.refresh_from_db()

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(response.data["auth_token"], user.auth_token.key)
        self.assertNotEqual(user.last_login, previous_last_login)
        self.assertTrue(self.signal_sent)

    def test_post_should_not_login_if_user_is_not_active(self):
        """
        In Django >= 1.10 authenticate() returns None if
        user is inactive, while in Django < 1.10 authenticate()
        succeeds if user is inactive.
        """
        user = create_user()
        data = {"username": user.username, "password": user.raw_password}
        user.is_active = False
        user.save()
        user_logged_in.connect(self.signal_receiver)

        response = self.client.post(self.base_url, data)

        if django.VERSION >= (1, 10):
            expected_errors = [settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR]
        else:
            expected_errors = [settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR]

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"], expected_errors)
        self.assertFalse(self.signal_sent)

    def test_post_should_not_login_if_invalid_credentials(self):
        user = create_user()
        data = {"username": user.username, "password": "wrong"}
        user_login_failed.connect(self.signal_receiver)

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"],
            [settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR],
        )
        self.assertTrue(self.signal_sent)

    def test_post_should_not_login_if_empty_request(self):
        data = {}

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"],
            [settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR],
        )
