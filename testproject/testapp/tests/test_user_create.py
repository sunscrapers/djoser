import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test.utils import override_settings
from django.core import mail
from importlib.metadata import version
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser, ExampleUser

from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.mark.django_db
class TestUserCreateView:
    def test_post_create_user_without_login(self, anonymous_api_client):
        url = reverse("user-list")
        data = {"username": "john", "password": "secret", "csrftoken": "asdf"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert User.objects.filter(username=data["username"]).exists()
        user = User.objects.get(username=data["username"])
        assert user.check_password(data["password"])

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_post_create_user_with_login_and_send_activation_email(
        self, anonymous_api_client
    ):
        url = reverse("user-list")
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data["username"]).exists()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data["email"]]

        user = User.objects.get(username="john")
        assert not user.is_active

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{"SEND_ACTIVATION_EMAIL": False, "SEND_CONFIRMATION_EMAIL": True},
        )
    )
    def test_post_create_user_with_login_and_send_confirmation_email(
        self, anonymous_api_client
    ):
        url = reverse("user-list")
        data = {"username": "john", "email": "john@beatles.com", "password": "secret"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=data["username"]).exists()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data["email"]]

        user = User.objects.get(username="john")
        assert user.is_active

    def test_post_not_create_new_user_if_username_exists(
        self, anonymous_api_client, user
    ):
        url = reverse("user-list")
        data = {"username": user.username, "password": "secret", "csrftoken": "asdf"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_not_register_if_fails_password_validation(self, anonymous_api_client):
        url = reverse("user-list")
        data = {"username": "paul", "password": "666", "csrftoken": "asdf"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert str(response.data["password"][0]) == "Password 666 is not allowed."
        if version("djangorestframework") >= "3.9.0":
            assert response.data["password"][0].code == "no666"

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USER_CREATE_PASSWORD_RETYPE": True})
    )
    def test_post_not_register_if_password_mismatch(self, anonymous_api_client):
        url = reverse("user-list")
        data = {
            "username": "paul",
            "password": "secret",
            "re_password": "wrong",
            "csrftoken": "asdf",
        }
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert (
            str(response.data["non_field_errors"][0])
            == default_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
        )

    def test_post_return_400_for_integrity_error(self, anonymous_api_client, mocker):
        url = reverse("user-list")

        def perform_create_mock(x):
            raise IntegrityError

        mocker.patch(
            "djoser.serializers.UserCreateSerializer.perform_create",
            side_effect=perform_create_mock,
        )
        data = {"username": "paul", "email": "paul@beatles.com", "password": "secret"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == [
            default_settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
        ]

    @override_settings(AUTH_USER_MODEL="testapp.CustomUser")
    def test_post_create_custom_user_with_all_required_fields(
        self, anonymous_api_client, mocker
    ):
        url = reverse("user-list")
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
        mocker.patch(
            "djoser.serializers.UserCreateSerializer.Meta.fields",
            tuple(CustomUser.REQUIRED_FIELDS)
            + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
        )
        mocker.patch("djoser.views.User", CustomUser)

        data = {
            "custom_username": "ringo",
            "password": "secret",
            "custom_required_field": "42",
        }
        response = anonymous_api_client.post(url, data)

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

    @override_settings(AUTH_USER_MODEL="testapp.CustomUser")
    def test_post_not_create_custom_user_with_missing_required_fields(
        self, anonymous_api_client, mocker
    ):
        url = reverse("user-list")
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.serializers.UserCreateSerializer.Meta.model", CustomUser)
        mocker.patch(
            "djoser.serializers.UserCreateSerializer.Meta.fields",
            tuple(CustomUser.REQUIRED_FIELDS)
            + (CustomUser.USERNAME_FIELD, CustomUser._meta.pk.name, "password"),
        )
        mocker.patch("djoser.views.User", CustomUser)

        data = {"custom_username": "ringo", "password": "secret"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response.render()
        assert response.data["custom_required_field"][0].code == "required"

    @override_settings(AUTH_USER_MODEL="testapp.ExampleUser")
    def test_post_create_custom_user_without_username(
        self, anonymous_api_client, mocker
    ):
        url = reverse("user-list")
        mocker.patch("djoser.serializers.User", ExampleUser)
        mocker.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
        mocker.patch(
            "djoser.serializers.UserCreateSerializer.Meta.fields",
            tuple(ExampleUser.REQUIRED_FIELDS)
            + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
        )
        mocker.patch("djoser.views.User", ExampleUser)

        data = {"password": "secret", "email": "test@user1.com"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert ExampleUser.objects.filter(email=data["email"]).exists()
        user = ExampleUser.objects.get(email=data["email"])
        assert user.check_password(data["password"])

    @override_settings(AUTH_USER_MODEL="testapp.ExampleUser")
    def test_post_create_custom_user_missing_required_fields(
        self, anonymous_api_client, mocker
    ):
        url = reverse("user-list")
        mocker.patch("djoser.serializers.User", ExampleUser)
        mocker.patch("djoser.serializers.UserCreateSerializer.Meta.model", ExampleUser)
        mocker.patch(
            "djoser.serializers.UserCreateSerializer.Meta.fields",
            tuple(ExampleUser.REQUIRED_FIELDS)
            + (ExampleUser.USERNAME_FIELD, ExampleUser._meta.pk.name, "password"),
        )
        mocker.patch("djoser.views.User", ExampleUser)

        data = {"password": "secret"}
        response = anonymous_api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["email"][0].code == "required"

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"USER_CREATE_PASSWORD_RETYPE": True})
    )
    def test_user_create_with_retype_password(self, anonymous_api_client):
        url = reverse("user-list")
        data = {"username": "paul", "password": "secret", "re_password": "secret"}
        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
