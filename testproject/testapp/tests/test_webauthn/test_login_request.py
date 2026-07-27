import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from .utils import create_credential_options

User = get_user_model()


@pytest.mark.django_db
class TestLoginRequestView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("webauthn_login_request")

    def test_post_with_non_existing_username_should_return_400(
        self, api_client, djoser_settings
    ):
        djoser_settings["LOGIN_FIELD"] = "username"
        data = {"username": "john"}
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_username_not_registered_with_webauthn_should_return_400(
        self, api_client, user, djoser_settings
    ):
        djoser_settings["LOGIN_FIELD"] = "username"
        data = {"username": user.username}
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_username_registered_with_webauthn_should_return_login_assertion(
        self, api_client, djoser_settings
    ):
        djoser_settings["LOGIN_FIELD"] = "username"
        co = create_credential_options(with_user=True)
        data = {"username": co.username}
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
