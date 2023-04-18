from django.conf import settings
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.models import CustomUser
from testapp.tests.common import create_user, mock

from djoser.compat import get_user_email
from djoser.conf import settings as default_settings


class TestResendActivationEmail(
    APITestCase, assertions.EmailAssertionsMixin, assertions.StatusCodeAssertionsMixin
):
    def setUp(self):
        self.base_url = reverse("user-resend-activation")

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_resend_activation_view(self):
        user = create_user(is_active=False)
        data = {"email": user.email}
        response = self.client.post(self.base_url, data)

        self.assert_email_exists(to=[user.email])
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_dont_resend_activation_when_disabled(self):
        user = create_user(is_active=False)
        data = {"email": user.email}
        response = self.client.post(self.base_url, data)

        self.assert_emails_in_mailbox(0)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_dont_resend_activation_when_active(self):
        user = create_user(is_active=True)
        data = {"email": user.email}
        response = self.client.post(self.base_url, data)

        self.assert_emails_in_mailbox(0)
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_dont_resend_activation_when_no_password(self):
        user = create_user(is_active=False, password=None)
        data = {"email": user.email}
        response = self.client.post(self.base_url, data)

        self.assert_emails_in_mailbox(0)
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.views.User", CustomUser)
    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}),
    )
    def test_resend_activation_view_custom_user(self):
        user = create_user(use_custom_data=True, is_active=False)
        data = {"custom_email": get_user_email(user)}
        response = self.client.post(self.base_url, data)

        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[get_user_email(user)])
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_post_should_return_no_content_if_user_does_not_exist(self):
        data = {"email": "john@beatles.com"}

        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"RESEND_ACTIVATION_SHOW_EMAIL_NOT_FOUND": True})
    )
    def test_post_should_return_bad_request_if_user_does_not_exist(self):
        data = {"email": "john@beatles.com"}

        response = self.client.post(self.base_url, data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()[0], default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND
        )