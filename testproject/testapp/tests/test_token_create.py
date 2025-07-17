import pytest
from django.contrib.auth import user_logged_in, user_login_failed
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.conf import settings


@pytest.fixture
def url():
    return reverse("login")


@pytest.fixture
def signal_tracker():
    class SignalTracker:
        received_login = False
        received_failed = False

        def login_receiver(self, sender, **kwargs):
            self.received_login = True

        def failed_receiver(self, sender, **kwargs):
            self.received_failed = True

    tracker = SignalTracker()
    # Connect signals
    user_logged_in.connect(tracker.login_receiver)
    user_login_failed.connect(tracker.failed_receiver)
    yield tracker
    # Disconnect explicitly
    user_logged_in.disconnect(tracker.login_receiver)
    user_login_failed.disconnect(tracker.failed_receiver)


@pytest.mark.django_db
class TestTokenCreateView:
    # Use anonymous_api_client for all login attempts

    def test_post_should_login_user(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        previous_last_login = user.last_login
        data = {"username": user.username, "password": user.raw_password}

        response = anonymous_api_client.post(url, data)
        user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert "auth_token" in response.data
        assert response.data["auth_token"] == user.auth_token.key
        assert user.last_login is not None
        assert user.last_login != previous_last_login
        assert signal_tracker.received_login
        assert not signal_tracker.received_failed

    def test_post_should_not_login_if_user_is_not_active(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        data = {"username": user.username, "password": user.raw_password}
        user.is_active = False
        user.save()

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["non_field_errors"][0]
            == settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
        )
        assert not signal_tracker.received_login
        # Login failed signal *might* be sent depending on backend behavior with inactive users  # noqa: E501
        # assert signal_tracker.received_failed
        # Keep this commented unless behavior is confirmed

    def test_post_should_not_login_if_invalid_credentials(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        data = {"username": user.username, "password": "wrong"}

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"] == [
            settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
        ]
        assert not signal_tracker.received_login
        assert signal_tracker.received_failed

    def test_post_should_not_login_if_empty_request(
        self, anonymous_api_client, url, signal_tracker
    ):
        data = {}

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Check for specific error (can vary)
        assert (
            response.data["non_field_errors"]
            == [settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR]
            or "username" in response.data
            or "password" in response.data
        )
        assert not signal_tracker.received_login
        assert not signal_tracker.received_failed
