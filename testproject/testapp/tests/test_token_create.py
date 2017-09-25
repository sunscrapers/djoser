from django.contrib.auth import user_logged_in, user_login_failed
from djet import assertions, restframework
from rest_framework import status
import django
import djoser.constants
import djoser.utils
import djoser.views

from .common import create_user


class TokenCreateViewTest(restframework.APIViewTestCase,
                          assertions.StatusCodeAssertionsMixin,
                          assertions.InstanceAssertionsMixin):
    view_class = djoser.views.TokenCreateView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_login_user(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': user.raw_password,
        }
        user_logged_in.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(response.data['auth_token'], user.auth_token.key)
        self.assertTrue(self.signal_sent)

    def test_post_should_not_login_if_user_is_not_active(self):
        """
        In Django >= 1.10 authenticate() returns None if
        user is inactive, while in Django < 1.10 authenticate()
        succeeds if user is inactive.
        """
        user = create_user()
        data = {
            'username': user.username,
            'password': user.raw_password,
        }
        user.is_active = False
        user.save()
        user_logged_in.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        if django.VERSION >= (1, 10):
            expected_errors = [djoser.constants.INVALID_CREDENTIALS_ERROR]
        else:
            expected_errors = [djoser.constants.INACTIVE_ACCOUNT_ERROR]

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], expected_errors)
        self.assertFalse(self.signal_sent)

    def test_post_should_not_login_if_invalid_credentials(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': 'wrong',
        }
        user_login_failed.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'],
            [djoser.constants.INVALID_CREDENTIALS_ERROR]
        )
        self.assertTrue(self.signal_sent)

    def test_post_should_not_login_if_empty_request(self):
        data = {}
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'],
            [djoser.constants.INVALID_CREDENTIALS_ERROR]
        )
