import pytest
import importlib

from django.conf import settings
from django.contrib.auth import HASH_SESSION_KEY
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.conf import settings as djoser_settings

Token = djoser_settings.TOKEN_MODEL


class TestSetPasswordView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("user-set-password")

    def test_post_set_new_password(self, authenticated_client, user, mailoutbox):
        data = {"new_password": "new password", "current_password": "secret"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mailoutbox) == 0

    def test_post_set_new_password_with_retype(
        self, authenticated_client, user, mailoutbox, djoser_settings
    ):
        djoser_settings["SET_PASSWORD_RETYPE"] = True
        data = {
            "new_password": "new password",
            "re_new_password": "new password",
            "current_password": "secret",
        }

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mailoutbox) == 0

    def test_post_not_set_new_password_if_wrong_current_password(
        self, authenticated_client, user
    ):
        data = {"new_password": "new password", "current_password": "wrong"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_not_set_new_password_if_mismatch(
        self, authenticated_client, user, djoser_settings
    ):
        djoser_settings["SET_PASSWORD_RETYPE"] = True
        data = {
            "new_password": "new password",
            "re_new_password": "wrong",
            "current_password": "secret",
        }

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password(data["current_password"])

    def test_post_not_set_new_password_if_fails_validation(
        self, authenticated_client, user
    ):
        data = {
            "new_password": "666",
            "re_new_password": "666",
            "current_password": "secret",
        }

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"new_password": ["Password 666 is not allowed."]}

    def test_post_logout_after_password_change(
        self, djoser_settings, authenticated_client, user
    ):
        djoser_settings["LOGOUT_ON_PASSWORD_CHANGE"] = True
        data = {"new_password": "new password", "current_password": "secret"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        is_logged = Token.objects.filter(user=user).exists()
        assert not is_logged

    def test_post_not_logout_after_password_change_if_setting_is_false(
        self, djoser_settings, authenticated_client, user
    ):
        djoser_settings["LOGOUT_ON_PASSWORD_CHANGE"] = False
        data = {"new_password": "new password", "current_password": "secret"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        is_logged = Token.objects.filter(user=user).exists()
        assert is_logged

    def test_post_password_changed_confirmation_email(
        self, djoser_settings, authenticated_client, user, mailoutbox
    ):
        djoser_settings["PASSWORD_CHANGED_EMAIL_CONFIRMATION"] = True
        data = {"new_password": "new password", "current_password": "secret"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.check_password(data["new_password"])
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]

    def test_post_logout_with_confirmation_email_if_session_created(
        self, djoser_settings, authenticated_client, user
    ):
        djoser_settings["PASSWORD_CHANGED_EMAIL_CONFIRMATION"] = True
        djoser_settings["LOGOUT_ON_PASSWORD_CHANGE"] = True
        djoser_settings["CREATE_SESSION_ON_LOGIN"] = True
        data = {"new_password": "new password", "current_password": "secret"}

        response = authenticated_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        is_logged = Token.objects.filter(user=user).exists()
        assert not is_logged

    def test_post_logout_cycle_session(self, djoser_settings, api_client, db):
        djoser_settings["LOGOUT_ON_PASSWORD_CHANGE"] = False
        djoser_settings["CREATE_SESSION_ON_LOGIN"] = True
        from testapp.factories import UserFactory

        user = UserFactory.create()
        data = {"new_password": "new password", "current_password": "secret"}
        api_client.force_authenticate(user=user)
        api_client.force_login(user)

        response = api_client.post(self.base_url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        user.refresh_from_db()

        session_id = api_client.cookies["sessionid"].coded_value
        engine = importlib.import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_id)
        session_key = session[HASH_SESSION_KEY]

        assert session_key == user.get_session_auth_hash()
