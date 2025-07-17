import pytest
from django.conf import settings
from django.contrib.auth import user_logged_out
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.fixture
def url():
    return reverse("logout")


@pytest.fixture
def signal_tracker():
    class SignalTracker:
        def __init__(self):
            self.received = False

        def signal_receiver(self, sender, **kwargs):
            self.received = True

    tracker = SignalTracker()
    user_logged_out.connect(tracker.signal_receiver)
    yield tracker
    user_logged_out.disconnect(tracker.signal_receiver)


@pytest.mark.django_db
class TestTokenDestroyView:
    def test_post_should_logout_logged_in_user(
        self, api_client, user, url, signal_tracker
    ):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert signal_tracker.received

    def test_post_should_deny_logging_out_when_user_not_logged_in(
        self, anonymous_api_client, user, url
    ):
        response = anonymous_api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_options(self, api_client, user, url):
        response = api_client.options(url)
        assert response.status_code == status.HTTP_200_OK

    @override_settings(DJOSER=dict(settings.DJOSER, **{"TOKEN_MODEL": None}))
    def test_none_token_model_results_in_no_operation(
        self, api_client, user, url, signal_tracker
    ):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert not signal_tracker.received
