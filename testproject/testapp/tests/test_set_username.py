from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from testapp.models import CustomUser
from testapp.tests.common import create_user, login_user, mock

User = get_user_model()


class SetUsernameViewTest(
    APITestCase, assertions.EmailAssertionsMixin, assertions.StatusCodeAssertionsMixin
):
    def setUp(self):
        self.base_url = reverse("user-set-{}".format(User.USERNAME_FIELD))

    def test_post_set_new_username(self):
        user = create_user()
        data = {"new_username": "ringo", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(data["new_username"], user.username)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_USERNAME_RETYPE": True}))
    def test_post_not_set_new_username_if_mismatch(self):
        user = create_user()
        data = {
            "new_username": "ringo",
            "re_new_username": "wrong",
            "current_password": "secret",
        }
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(data["new_username"], user.username)

    def test_post_not_set_new_username_if_exists(self):
        username = "tom"
        create_user(username=username)
        user = create_user(username="john")
        data = {"new_username": username, "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(user.username, username)

    def test_post_not_set_new_username_if_invalid(self):
        user = create_user()
        data = {"new_username": "$ wrong username #", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data["new_username"])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USERNAME_CHANGED_EMAIL_CONFIRMATION": True})
    )
    def test_post_update_username_and_send_activation_email(self):
        user = create_user()
        data = {"new_username": "dango", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])

    def test_post_not_set_new_username_if_same(self):
        user = create_user()
        data = {"new_username": "john", "current_password": "secret"}
        login_user(self.client, user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(user.is_active)

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.SetUsernameSerializer.Meta.fields",
        (CustomUser.USERNAME_FIELD, "custom_username"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(settings.DJOSER, **{"LOGIN_FIELD": CustomUser.USERNAME_FIELD}),
    )
    def test_post_set_new_custom_username(self):
        user = create_user(use_custom_data=True)
        data = {"new_custom_username": "ringo", "current_password": "secret"}
        self.client.force_authenticate(user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(data["new_custom_username"], user.get_username())

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.SetUsernameSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.SetUsernameSerializer.Meta.fields",
        (CustomUser.USERNAME_FIELD, "custom_username"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(
            settings.DJOSER,
            **{"SET_USERNAME_RETYPE": True, "LOGIN_FIELD": CustomUser.USERNAME_FIELD},
        ),
    )
    def test_post_not_set_new_custom_username_if_mismatch(self):
        user = create_user(use_custom_data=True)
        data = {
            "new_custom_username": "ringo",
            "re_new_custom_username": "wrong",
            "current_password": "secret",
        }
        self.client.force_authenticate(user)

        response = self.client.post(self.base_url, data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertNotEqual(data["new_custom_username"], user.get_username())
