import pytest
from django.conf import settings
from django.contrib.auth import HASH_SESSION_KEY, get_user_model
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.conf import settings as djoser_settings

User = get_user_model()
Token = djoser_settings.TOKEN_MODEL


@pytest.fixture
def url():
    return reverse("user-set-password")


@pytest.mark.django_db
class TestSetPasswordView:
    def test_post_set_new_password(self, api_client, user, url):
        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mail.outbox) == 0

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_PASSWORD_RETYPE": True}))
    def test_post_set_new_password_with_retype(self, api_client, user, url):
        data = {
            "new_password": "new password",
            "re_new_password": "new password",
            "current_password": "secret",
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mail.outbox) == 0

    def test_post_not_set_new_password_if_wrong_current_password(
        self, api_client, user, url
    ):
        data = {"new_password": "new password", "current_password": "wrong"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current_password" in response.data

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_PASSWORD_RETYPE": True}))
    def test_post_not_set_new_password_if_mismatch(self, api_client, user, url):
        original_password = "secret"
        data = {
            "new_password": "new password",
            "re_new_password": "wrong",
            "current_password": original_password,
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        user.refresh_from_db()
        assert user.check_password(original_password)

    def test_post_not_set_new_password_if_fails_validation(self, api_client, user, url):
        original_password = "secret"
        data = {
            "new_password": "666",
            "current_password": original_password,
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        user.refresh_from_db()
        assert user.check_password(original_password)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"LOGOUT_ON_PASSWORD_CHANGE": True})
    )
    def test_post_logout_after_password_change(self, api_client, user, url):
        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        if Token:
            assert not Token.objects.filter(user=user).exists()
        assert HASH_SESSION_KEY not in api_client.session

    def test_post_not_logout_after_password_change_if_setting_is_false(
        self, api_client, user, url
    ):
        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        if Token:
            assert Token.objects.filter(user=user).exists()
        assert HASH_SESSION_KEY in api_client.session

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_password_changed_confirmation_email(self, api_client, user, url):
        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{
                "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
                "LOGOUT_ON_PASSWORD_CHANGE": True,
                "CREATE_SESSION_ON_LOGIN": True,
            },
        )
    )
    def test_post_logout_with_confirmation_email_if_session_used(
        self, api_client, user, url
    ):
        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        if Token:
            assert not Token.objects.filter(user=user).exists()
        assert HASH_SESSION_KEY not in api_client.session
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{"LOGOUT_ON_PASSWORD_CHANGE": False, "CREATE_SESSION_ON_LOGIN": True},
        )
    )
    def test_post_logout_cycle_session(self, api_client, user, url):
        assert HASH_SESSION_KEY in api_client.session
        original_session_key = api_client.session.session_key

        data = {"new_password": "new password", "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        user.refresh_from_db()

        assert HASH_SESSION_KEY in api_client.session
        assert api_client.session[HASH_SESSION_KEY] == user.get_session_auth_hash()
        assert api_client.session[HASH_SESSION_KEY] != original_session_key
