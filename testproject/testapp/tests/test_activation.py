import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.signals
import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.fixture
def user(user):
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def url():
    return reverse("user-activation")


@pytest.fixture
def signal_tracker():
    class SignalTracker:
        received = False

        def signal_receiver(self, sender, **kwargs):
            self.received = True

    tracker = SignalTracker()
    djoser.signals.user_activated.connect(tracker.signal_receiver)
    yield tracker
    djoser.signals.user_activated.disconnect(tracker.signal_receiver)


@pytest.mark.django_db
class TestActivationView:
    def test_post_activate_user_and_not_login(self, anonymous_api_client, user, url):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
        }

        response = anonymous_api_client.post(url, data)
        user.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert user.is_active

    def test_post_respond_with_bad_request_when_wrong_uid(
        self, anonymous_api_client, user, url
    ):
        token = default_token_generator.make_token(user)
        data = {"uid": "wrong-uid", "token": token}

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert list(response.data.keys()) == ["uid"]
        assert response.data["uid"] == [
            default_settings.CONSTANTS.messages.INVALID_UID_ERROR
        ]

    def test_post_respond_with_403_when_already_active(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        user.is_active = True
        user.save()

        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert list(response.data.keys()) == ["detail"]
        assert (
            response.data["detail"]
            == default_settings.CONSTANTS.messages.STALE_TOKEN_ERROR
        )
        assert not signal_tracker.received

    def test_post_respond_with_bad_request_when_wrong_token(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        uid = djoser.utils.encode_uid(user.pk)
        data = {"uid": uid, "token": "wrong-token"}

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert list(response.data.keys()) == ["token"]
        assert response.data["token"] == [
            default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR
        ]
        assert not signal_tracker.received

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"SEND_CONFIRMATION_EMAIL": True})
    )
    def test_post_sent_confirmation_email(
        self, anonymous_api_client, user, url, signal_tracker
    ):
        uid = djoser.utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        data = {
            "uid": uid,
            "token": token,
        }

        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        assert signal_tracker.received
        user.refresh_from_db()
        assert user.is_active
