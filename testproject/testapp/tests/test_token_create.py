import pytest
from django.contrib.auth import user_logged_in, user_login_failed
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.conf import settings


@pytest.mark.django_db
class TestTokenCreateView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("login")

    def test_post_should_login_user(self, api_client, user, signal_tracker):
        previous_last_login = user.last_login
        data = {"username": user.username, "password": user.raw_password}
        user_logged_in.connect(signal_tracker.receiver)

        response = api_client.post(self.base_url, data)
        user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert response.data["auth_token"] == user.auth_token.key
        assert user.last_login != previous_last_login
        assert signal_tracker.signal_sent

    def test_post_should_not_login_if_user_is_not_active(
        self, api_client, inactive_user, signal_tracker
    ):
        """
        In Django >= 1.10 authenticate() returns None if user is inactive, while in
        Django < 1.10 authenticate() succeeds if user is inactive.
        """
        data = {
            "username": inactive_user.username,
            "password": inactive_user.raw_password,
        }
        user_logged_in.connect(signal_tracker.receiver)

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["non_field_errors"][0]
            == settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
        )
        assert not signal_tracker.signal_sent

    def test_post_should_not_login_if_invalid_credentials(
        self, api_client, user, signal_tracker
    ):
        data = {"username": user.username, "password": "wrong"}
        user_login_failed.connect(signal_tracker.receiver)

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"] == [
            settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
        ]
        assert signal_tracker.signal_sent

    def test_post_should_not_login_if_empty_request(self, api_client):
        data = {}

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"] == [
            settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
        ]
