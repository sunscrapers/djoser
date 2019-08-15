from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions
from pkg_resources import parse_version
from rest_framework import __version__ as drf_version
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from djoser.conf import settings as default_settings
from testapp.models import CustomUser, ExampleUser
from testapp.tests.common import create_user, mock, perform_create_mock

User = get_user_model()


class UserCreateViewTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    def setUp(self):
        self.base_url = reverse("user-list")  # /auth/users/

    def test_post_create_user_without_login(self):
        data = {"username": "john", "password": "secret", "csrftoken": "asdf"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue("password" not in response.data)
        self.assert_instance_exists(User, username=data["username"])
        user = User.objects.get(username=data["username"])
        self.assertTrue(user.check_password(data["password"]))

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_post_create_user_with_login_and_send_activation_email(self):
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data["username"])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data["email"]])

        user = User.objects.get(username="john")
        self.assertFalse(user.is_active)

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{"SEND_ACTIVATION_EMAIL": False, "SEND_CONFIRMATION_EMAIL": True},
        )
    )
    def test_post_create_user_with_login_and_send_confirmation_email(self):
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data["username"])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data["email"]])

        user = User.objects.get(username="john")
        self.assertTrue(user.is_active)

    def test_post_not_create_new_user_if_username_exists(self):
        create_user(username="john")
        data = {"username": "john", "password": "secret", "csrftoken": "asdf"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_not_register_if_fails_password_validation(self):
        data = {"username": "john", "password": "666", "csrftoken": "asdf"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response.render()
        self.assertEqual(
            str(response.data["password"][0]), "Password 666 is not allowed."
        )
        if parse_version(drf_version) >= parse_version("3.9.0"):
            self.assertEqual(response.data["password"][0].code, "no666")

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USER_CREATE_PASSWORD_RETYPE": True})
    )
    def test_post_not_register_if_password_mismatch(self):
        data = {
            "username": "john",
            "password": "secret",
            "re_password": "wrong",
            "csrftoken": "asdf",
        }
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response.render()
        self.assertEqual(
            str(response.data["non_field_errors"][0]),
            default_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR,
        )

    @mock.patch(
        "djoser.serializers.UserCreateSerializer.perform_create",
        side_effect=perform_create_mock,
    )
    def test_post_return_400_for_integrity_error(self, perform_create):
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [default_settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR],
        )

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(CustomUser.REQUIRED_FIELDS)
        + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @override_settings(AUTH_USER_MODEL="testapp.CustomUser")
    def test_post_create_custom_user_with_all_required_fields(self):
        data = {
            "custom_username": "john",
            "password": "secret",
            "custom_required_field": "42",
        }
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue("password" not in response.data)
        custom_user_model = get_user_model()
        self.assert_instance_exists(
            custom_user_model, custom_username=data[custom_user_model.USERNAME_FIELD]
        )
        user = custom_user_model.objects.get(
            custom_username=data[custom_user_model.USERNAME_FIELD]
        )
        self.assertTrue(user.check_password(data["password"]))

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(CustomUser.REQUIRED_FIELDS)
        + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @override_settings(AUTH_USER_MODEL="testapp.CustomUser")
    def test_post_not_create_custom_user_with_missing_required_fields(self):
        data = {"custom_username": "john", "password": "secret"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response.render()
        self.assertEqual(response.data["custom_required_field"][0].code, "required")

    @mock.patch("djoser.serializers.User", ExampleUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(ExampleUser.REQUIRED_FIELDS)
        + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", ExampleUser)
    @override_settings(AUTH_USER_MODEL="testapp.ExampleUser")
    def test_post_create_custom_user_without_username(self):
        data = {"password": "secret", "email": "test@user1.com"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue("password" not in response.data)
        self.assert_instance_exists(ExampleUser, email=data["email"])
        user = ExampleUser.objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))

    @mock.patch("djoser.serializers.User", ExampleUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(ExampleUser.REQUIRED_FIELDS)
        + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", ExampleUser)
    @override_settings(AUTH_USER_MODEL="testapp.ExampleUser")
    def test_post_create_custom_user_missing_required_fields(self):
        data = {"password": "secret"}
        response = self.client.post(self.base_url, data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0].code, "required")

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USER_CREATE_PASSWORD_RETYPE": True})
    )
    def test_user_create_with_retype_password(self):
        # GIVEN user is required to retype password
        # (see decorator)
        # WHEN sent correctly retyped password
        data = {"username": "john", "password": "secret", "re_password": "secret"}
        response = self.client.post(self.base_url, data)
        # THEN I get correct response
        self.assert_status_equal(response, status.HTTP_201_CREATED)
