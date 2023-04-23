from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user
from django.conf import settings
from django.test.utils import override_settings

User = get_user_model()

class TestPasswordlessEmailTokenRequest(APITestCase, assertions.StatusCodeAssertionsMixin):
    url = reverse("passwordless_email_signup_request")

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
          "PASSWORDLESS": {"REGISTER_NONEXISTENT_USERS": False}
        })
    )
    def test_post_with_non_existing_user_should_return_400_if_registration_disabled(self):
        data = {"email": "super@duper.com"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
          "PASSWORDLESS": {"REGISTER_NONEXISTENT_USERS": True}
        })
    )
    def test_post_request_with_new_user_successful_with_registration_enabled(self):
        data = {"email": "super@duper.com"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_post_request_with_existing_user_successful(self):
        user = create_user()
        data = {"email": user.email}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)