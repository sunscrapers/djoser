import pytest

# Remove djet
# from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse

# Remove APITestCase
# from rest_framework.test import APITestCase

from djoser.webauthn.models import CredentialOptions


@pytest.fixture
def url():
    return reverse("webauthn_signup_request")


@pytest.mark.django_db
class TestSignupRequestView:
    # Removed APITestCase and mixins

    def test_post_with_duplicate_username_should_fail(
        self, anonymous_api_client, user, url
    ):
        data = {"username": user.username, "display_name": user.username}
        response = anonymous_api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Optionally check the error message if consistent
        assert "username" in response.data

    def test_post_should_create_credential_options(self, anonymous_api_client, url):
        username = "john"
        data = {"username": username, "display_name": "John Doe"}
        response = anonymous_api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert CredentialOptions.objects.filter(username=username).exists()
        # Optionally check response content format
        assert "publicKey" in response.data
        assert "challenge" in response.data["publicKey"]
