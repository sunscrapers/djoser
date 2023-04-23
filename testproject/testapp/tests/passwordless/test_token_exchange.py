from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user
from django.conf import settings
from django.test.utils import override_settings
from .utils import create_token

User = get_user_model()

class TestPasswordlessTokenExchange(APITestCase, assertions.StatusCodeAssertionsMixin):
    url = reverse("passwordless_token_exchange")

    def test_should_fail_with_dummy_token(self):
        data = {"token": "dubidubidu"}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_should_fail_with_short_token(self):
        token = create_token("email")
        data = {"token": token.short_token}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_should_accept_long_token_standalone(self):
        token = create_token("email")
        data = {"token": token.token}
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_should_accept_short_token_when_same_info_included(self):
        token = create_token("email")
        data = {
            "token": token.token,
            "email": token.user.email
            }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
          "PASSWORDLESS": {"MAX_TOKEN_USES": 1}
        })
    )
    def test_should_allow_redeeming_token_only_limited_times(self):
        token = create_token("email")
        data = {
            "token": token.token,
            "email": token.user.email
            }
        response = self.client.post(self.url, data=data)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
          "PASSWORDLESS": {"MAX_TOKEN_USES": 2}
        })
    )
    def test_should_allow_redeeming_token_only_limited_times(self):
        token = create_token("email")
        data = {
            "token": token.token,
            "email": token.user.email
        }
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response = self.client.post(self.url, data=data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)