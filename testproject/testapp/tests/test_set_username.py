import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail  # Import mail for email assertions
from django.test.utils import override_settings

# Remove djet assertions
# from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse

# Remove APITestCase
# from rest_framework.test import APITestCase
from testapp.models import CustomUser

User = get_user_model()


@pytest.fixture
def url():
    username_field = User.USERNAME_FIELD
    return reverse(f"user-set-{username_field}")


@pytest.fixture
def custom_url():
    username_field = CustomUser.USERNAME_FIELD
    return reverse(f"user-set-{username_field}")


@pytest.mark.django_db
class TestSetUsernameView:
    # Use api_client (authenticated as user) for all tests

    def test_post_set_new_username(self, api_client, user, url):
        data = {"new_username": "ringo", "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.username == data["new_username"]

    def test_post_not_set_new_username_if_wrong_current_password(
        self, api_client, user, url
    ):
        original_username = user.username
        data = {"new_username": "ringo", "current_password": "wrong"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["current_password"] == ["Invalid password."]
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_USERNAME_RETYPE": True}))
    def test_post_not_set_new_username_if_mismatch(self, api_client, user, url):
        original_username = user.username
        data = {
            "new_username": "ringo",
            "re_new_username": "wrong",
            "current_password": "secret",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    def test_post_not_set_new_username_if_exists(
        self, api_client, user, other_user, url
    ):
        original_username = user.username
        data = {"new_username": other_user.username, "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_username" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    def test_post_not_set_new_username_if_invalid(self, api_client, user, url):
        original_username = user.username
        data = {"new_username": "$ wrong username #", "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_username" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_update_username_and_send_confirmation_email(
        self, api_client, user, url
    ):
        data = {"new_username": "dango", "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        user.refresh_from_db()
        assert user.username == data["new_username"]

    def test_post_not_set_new_username_if_same(self, api_client, user, url):
        original_username = user.username
        data = {"new_username": original_username, "current_password": "secret"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_username" in response.data
        user.refresh_from_db()
        assert user.username == original_username

    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(settings.DJOSER, **{"LOGIN_FIELD": CustomUser.USERNAME_FIELD}),
    )
    def test_post_set_new_custom_username(
        self, api_client, custom_user, custom_url, mocker
    ):
        # Patching using mocker
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
        mocker.patch(
            "djoser.serializers.SetUsernameSerializer.Meta.fields",
            (
                CustomUser.USERNAME_FIELD,
                "new_" + CustomUser.USERNAME_FIELD,
            ),  # Correct field name
        )
        mocker.patch("djoser.views.User", CustomUser)

        # Use dynamic field names
        new_username_key = "new_" + CustomUser.USERNAME_FIELD
        data = {new_username_key: "ringo", "current_password": "secret"}

        # Authenticate as custom_user for this test
        api_client.force_authenticate(custom_user)

        response = api_client.post(custom_url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        custom_user.refresh_from_db()
        assert custom_user.get_username() == data[new_username_key]
        api_client.force_authenticate(None)  # Clean up

    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(
            settings.DJOSER,
            **{"SET_USERNAME_RETYPE": True, "LOGIN_FIELD": CustomUser.USERNAME_FIELD},
        ),
    )
    def test_post_not_set_new_custom_username_if_mismatch(
        self, api_client, custom_user, custom_url, mocker
    ):
        # Patching using mocker
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
        mocker.patch(
            "djoser.serializers.SetUsernameSerializer.Meta.fields",
            (
                CustomUser.USERNAME_FIELD,
                "new_" + CustomUser.USERNAME_FIELD,
                "re_new_" + CustomUser.USERNAME_FIELD,
            ),  # Correct field names
        )
        mocker.patch("djoser.views.User", CustomUser)

        original_username = custom_user.get_username()
        # Use dynamic field names
        new_username_key = "new_" + CustomUser.USERNAME_FIELD
        re_new_username_key = "re_new_" + CustomUser.USERNAME_FIELD
        data = {
            new_username_key: "ringo",
            re_new_username_key: "wrong",
            "current_password": "secret",
        }

        # Authenticate as custom_user for this test
        api_client.force_authenticate(custom_user)

        response = api_client.post(custom_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        custom_user.refresh_from_db()
        assert custom_user.get_username() == original_username
        api_client.force_authenticate(None)  # Clean up
