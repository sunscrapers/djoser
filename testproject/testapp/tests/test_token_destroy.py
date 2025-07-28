import pytest
from django.contrib.auth import user_logged_out
from rest_framework import status
from rest_framework.reverse import reverse


class TestTokenDestroyView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.signal_sent = False
        self.base_url = reverse("logout")

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_logout_logged_in_user(
        self, authenticated_client, signal_tracker
    ):
        user_logged_out.connect(signal_tracker.receiver)

        response = authenticated_client.post(self.base_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert signal_tracker.signal_sent

    def test_post_should_deny_logging_out_when_user_not_logged_in(self, api_client):
        response = api_client.post(self.base_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_options(self, authenticated_client):
        response = authenticated_client.options(self.base_url)

        assert response.status_code == status.HTTP_200_OK

    def test_none_token_model_results_in_no_operation(
        self, authenticated_client, djoser_settings
    ):
        djoser_settings["TOKEN_MODEL"] = None
        user_logged_out.connect(self.signal_receiver)

        response = authenticated_client.post(self.base_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert not self.signal_sent
