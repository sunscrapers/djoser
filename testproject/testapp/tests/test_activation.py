import pytest
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.signals
import djoser.utils
import djoser.views
from djoser.conf import settings as default_settings


@pytest.mark.django_db
class TestActivationView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("user-activation")

    def test_post_activate_user_and_not_login(self, api_client, user):
        user.is_active = False
        user.save()
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
        }

        response = api_client.post(self.base_url, data)
        user.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert user.is_active

    def test_post_respond_with_bad_request_when_wrong_uid(self, api_client, user):
        data = {"uid": "wrong-uid", "token": default_token_generator.make_token(user)}

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert list(response.data.keys()) == ["uid"]
        assert response.data["uid"] == [
            default_settings.CONSTANTS.messages.INVALID_UID_ERROR
        ]

    def test_post_respond_with_bad_request_when_stale_token(
        self, api_client, user, signal_tracker
    ):
        djoser.signals.user_activated.connect(signal_tracker.receiver)
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
        }

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert list(response.data.keys()) == ["detail"]
        assert (
            response.data["detail"]
            == default_settings.CONSTANTS.messages.STALE_TOKEN_ERROR
        )
        assert not signal_tracker.signal_sent

    def test_post_respond_with_bad_request_when_wrong_token(
        self, api_client, user, signal_tracker
    ):
        djoser.signals.user_activated.connect(signal_tracker.receiver)
        data = {"uid": djoser.utils.encode_uid(user.pk), "token": "wrong-token"}

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert list(response.data.keys()) == ["token"]
        assert response.data["token"] == [
            default_settings.CONSTANTS.messages.INVALID_TOKEN_ERROR
        ]
        assert not signal_tracker.signal_sent

    def test_post_sent_confirmation_email(
        self, djoser_settings, api_client, user, signal_tracker, mailoutbox
    ):
        djoser_settings["SEND_CONFIRMATION_EMAIL"] = True
        user.is_active = False
        user.save()
        djoser.signals.user_activated.connect(signal_tracker.receiver)
        data = {
            "uid": djoser.utils.encode_uid(user.pk),
            "token": default_token_generator.make_token(user),
        }

        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]
        assert signal_tracker.signal_sent
