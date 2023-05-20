from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user

from djoser.webauthn.models import CredentialOptions


class SignupRequestViewTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    url = reverse("webauthn_signup_request")

    def test_post_with_duplicate_username_should_fail(self):
        user = create_user()
        data = {"username": user.username, "display_name": user.username}
        response = self.client.post(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_should_create_credential_options(self):
        data = {"username": "john", "display_name": "John Doe"}
        response = self.client.post(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_instance_exists(CredentialOptions, username=data["username"])
