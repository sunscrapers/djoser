from django.conf import settings
from django.contrib.auth import user_logged_out
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from testapp.tests.common import create_user, login_user


class TokenDestroyViewTest(APITestCase, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        self.signal_sent = False
        self.base_url = reverse("logout")

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_logout_logged_in_user(self):
        user = create_user()
        user_logged_out.connect(self.signal_receiver)

        login_user(self.client, user)
        response = self.client.post(self.base_url)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
        self.assertTrue(self.signal_sent)

    def test_post_should_deny_logging_out_when_user_not_logged_in(self):
        create_user()
        response = self.client.post(self.base_url)

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_options(self):
        user = create_user()

        login_user(self.client, user)
        response = self.client.options(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"TOKEN_MODEL": None}))
    def test_none_token_model_results_in_no_operation(self):
        user = create_user()
        user_logged_out.connect(self.signal_receiver)

        login_user(self.client, user)
        response = self.client.post(self.base_url)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
        self.assertFalse(self.signal_sent)
