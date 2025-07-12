import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from .utils import create_credential_options

User = get_user_model()


@pytest.fixture
def credential_options(db, user):
    return create_credential_options(with_user=True, user=user)


@pytest.fixture
def url():
    return reverse("webauthn_login_request")


@pytest.mark.django_db
class TestLoginRequestView:
    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.DJOSER = {**settings.DJOSER, **{"LOGIN_FIELD": "username"}}
        return settings

    def test_post_with_non_existing_username_should_return_400(
        self, anonymous_api_client, url
    ):
        data = {"username": "non_existent_user"}
        response = anonymous_api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_username_not_registered_with_webauthn_should_return_400(
        self, anonymous_api_client, user, url
    ):
        data = {"username": user.username}
        response = anonymous_api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_username_registered_with_webauthn_should_return_login_assertion(
        self, anonymous_api_client, credential_options, url
    ):
        data = {"username": credential_options.username}
        response = anonymous_api_client.post(url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert "publicKey" in response.data
        assert "challenge" in response.data["publicKey"]
