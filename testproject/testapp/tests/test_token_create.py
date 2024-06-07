from django.conf import settings as django_settings
from unittest import mock

from django.contrib.auth import user_logged_in, user_login_failed
from django.contrib.auth.backends import ModelBackend
from django.test import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user

from djoser.conf import settings


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

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "django.contrib.auth.backends.ModelBackend",
        ]
    )
    @override_settings(
        DJOSER=dict(django_settings.DJOSER, **{"LOGIN_FIELD": "username"})
    )
    def test_login__LOGIN_FIELD_username__USERNAME_FIELD_username(
        self,
    ):
        user = create_user()
        user_logged_in.connect(self.signal_receiver)
        previous_last_login = user.last_login

        with mock.patch("djoser.serializers.User.USERNAME_FIELD", "username"):
            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_200_OK)

                user.refresh_from_db()
                self.assertEqual(response.data["auth_token"], user.auth_token.key)
                self.assertNotEqual(user.last_login, previous_last_login)
                self.assertTrue(self.signal_sent)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "django.contrib.auth.backends.ModelBackend",
        ]
    )
    @override_settings(DJOSER=dict(django_settings.DJOSER, **{"LOGIN_FIELD": "email"}))
    def test_login__LOGIN_FIELD_email__USERNAME_FIELD_username(
        self,
    ):
        user = create_user()
        user_logged_in.connect(self.signal_receiver)
        previous_last_login = user.last_login

        with mock.patch("djoser.serializers.User.USERNAME_FIELD", "username"):
            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

        user.refresh_from_db()
        self.assertEqual(user.last_login, previous_last_login)
        self.assertFalse(self.signal_sent)

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "django.contrib.auth.backends.ModelBackend",
        ]
    )
    @override_settings(
        DJOSER=dict(django_settings.DJOSER, **{"LOGIN_FIELD": "username"})
    )
    def test_login__LOGIN_FIELD_username__USERNAME_FIELD_email(
        self,
    ):
        user = create_user()
        user_logged_in.connect(self.signal_receiver)
        previous_last_login = user.last_login

        with mock.patch("djoser.serializers.User.USERNAME_FIELD", "email"):
            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

        user.refresh_from_db()
        self.assertEqual(user.last_login, previous_last_login)
        self.assertFalse(self.signal_sent)

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "django.contrib.auth.backends.ModelBackend",
        ]
    )
    @override_settings(DJOSER=dict(django_settings.DJOSER, **{"LOGIN_FIELD": "email"}))
    def test_login__LOGIN_FIELD_email__USERNAME_FIELD_email(
        self,
    ):
        user = create_user()
        user_logged_in.connect(self.signal_receiver)
        previous_last_login = user.last_login

        with mock.patch("djoser.serializers.User.USERNAME_FIELD", "email"):
            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url,
                    {"username": user.username, "password": user.raw_password},
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=True
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_200_OK)

                user.refresh_from_db()
                self.assertEqual(response.data["auth_token"], user.auth_token.key)
                self.assertNotEqual(user.last_login, previous_last_login)
                self.assertTrue(self.signal_sent)

            with mock.patch.object(
                ModelBackend, "user_can_authenticate", return_value=False
            ):
                response = self.client.post(
                    self.base_url, {"email": user.email, "password": user.raw_password}
                )
                self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_should_not_login_if_user_is_not_active(self):
        """In Django >= 1.10 authenticate() returns None if user is inactive,
        while in Django < 1.10 authenticate() succeeds if user is inactive."""
        user = create_user()
        data = {"username": user.username, "password": user.raw_password}
        user.is_active = False
        user.save()
        user_logged_in.connect(self.signal_receiver)

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        )
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
