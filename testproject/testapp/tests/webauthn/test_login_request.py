from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user

from .utils import create_credential_options

User = get_user_model()


class TestLoginRequestView(APITestCase, assertions.StatusCodeAssertionsMixin):
    url = reverse("webauthn_login_request")

    def test_post_with_non_existing_username_should_return_400(self):
        data = {"username": "john"}
        response = self.client.post(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_with_username_not_registered_with_webauthn_should_return_400(self):
        user = create_user()
        data = {"username": user.username}
        response = self.client.post(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_with_username_registered_with_webauthn_should_return_login_assertion(
        self,
    ):
        co = create_credential_options(with_user=True)
        data = {"username": co.username}
        response = self.client.post(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
