import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from importlib.metadata import version
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser, ExampleUser
from unittest import mock

from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.mark.django_db
class TestUserCreateView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("user-list")  # /auth/users/

    def test_post_create_user_without_login(self, api_client):
        data = {"username": "john", "password": "secret", "csrftoken": "asdf"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert User.objects.filter(username=data["username"]).exists()
        user = User.objects.get(username=data["username"])
        assert user.check_password(data["password"])

    def test_post_create_user_with_login_and_send_activation_email(
        self, api_client, mailoutbox, djoser_settings
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = True
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data["username"]).exists()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [data["email"]]

        user = User.objects.get(username="john")
        assert not user.is_active

    def test_post_create_user_with_login_and_send_confirmation_email(
        self, djoser_settings, api_client, mailoutbox
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = False
        djoser_settings["SEND_CONFIRMATION_EMAIL"] = True
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data["username"]).exists()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [data["email"]]

        user = User.objects.get(username="john")
        assert user.is_active

    def test_post_not_create_new_user_if_username_exists(self, api_client, user):
        data = {"username": user.username, "password": "secret", "csrftoken": "asdf"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_not_register_if_fails_password_validation(self, api_client):
        data = {"username": "john", "password": "666", "csrftoken": "asdf"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert str(response.data["password"][0]) == "Password 666 is not allowed."
        if version("djangorestframework") >= "3.9.0":
            assert response.data["password"][0].code == "no666"

    def test_post_not_register_if_password_mismatch(self, djoser_settings, api_client):
        djoser_settings["USER_CREATE_PASSWORD_RETYPE"] = True
        data = {
            "username": "john",
            "password": "secret",
            "re_password": "wrong",
            "csrftoken": "asdf",
        }
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert (
            str(response.data["non_field_errors"][0])
            == default_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
        )

    @mock.patch(
        "djoser.serializers.UserCreateSerializer.perform_create",
        side_effect=IntegrityError(),
    )
    def test_post_return_400_for_integrity_error(self, perform_create_mock, api_client):
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == [
            default_settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
        ]

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(CustomUser.REQUIRED_FIELDS)
        + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @pytest.mark.django_db(transaction=True)
    def test_post_create_custom_user_with_all_required_fields(
        self, api_client, settings
    ):
        settings.AUTH_USER_MODEL = "testapp.CustomUser"
        data = {
            "custom_username": "john",
            "password": "secret",
            "custom_required_field": "42",
        }
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        custom_user_model = get_user_model()
        assert custom_user_model.objects.filter(
            custom_username=data[custom_user_model.USERNAME_FIELD]
        ).exists()
        user = custom_user_model.objects.get(
            custom_username=data[custom_user_model.USERNAME_FIELD]
        )
        assert user.check_password(data["password"])

    @mock.patch("djoser.serializers.User", CustomUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(CustomUser.REQUIRED_FIELDS)
        + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", CustomUser)
    @pytest.mark.django_db(transaction=True)
    def test_post_not_create_custom_user_with_missing_required_fields(
        self, api_client, settings
    ):
        settings.AUTH_USER_MODEL = "testapp.CustomUser"
        data = {"custom_username": "john", "password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert response.data["custom_required_field"][0].code == "required"

    @mock.patch("djoser.serializers.User", ExampleUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(ExampleUser.REQUIRED_FIELDS)
        + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", ExampleUser)
    @pytest.mark.django_db(transaction=True)
    def test_post_create_custom_user_without_username(self, api_client, settings):
        settings.AUTH_USER_MODEL = "testapp.ExampleUser"
        data = {"password": "secret", "email": "test@user1.com"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert ExampleUser.objects.filter(email=data["email"]).exists()
        user = ExampleUser.objects.get(email=data["email"])
        assert user.check_password(data["password"])

    @mock.patch("djoser.serializers.User", ExampleUser)
    @mock.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
    @mock.patch(
        "djoser.serializers.UserCreateSerializer.Meta.fields",
        tuple(ExampleUser.REQUIRED_FIELDS)
        + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
    )
    @mock.patch("djoser.views.User", ExampleUser)
    @pytest.mark.django_db(transaction=True)
    def test_post_create_custom_user_missing_required_fields(
        self, api_client, settings
    ):
        settings.AUTH_USER_MODEL = "testapp.ExampleUser"
        data = {"password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["email"][0].code == "required"

    def test_user_create_with_retype_password(self, djoser_settings, api_client):
        djoser_settings["USER_CREATE_PASSWORD_RETYPE"] = True
        data = {"username": "john", "password": "secret", "re_password": "secret"}
        response = api_client.post(self.base_url, data)

        assert response.status_code == status.HTTP_201_CREATED
