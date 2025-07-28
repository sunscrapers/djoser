import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.views
from djoser.conf import settings as djoser_settings

from testapp.factories import UserFactory

User = get_user_model()


# Test-specific classes
class RunCheck(Exception):
    """Custom exception for testing."""

    pass


class PermCheckClass:
    """Mock permission class for testing."""

    def has_permission(self, *args, **kwargs):
        raise RunCheck("working")

    def has_object_permission(self, *args, **kwargs):
        raise RunCheck("working")


class SerializerCheckClass:
    """Mock serializer class for testing."""

    def __init__(self, *args, **kwargs):
        raise RunCheck("working")


class TestUserMeDeleteView:
    viewset = djoser.views.UserViewSet

    def test_delete_user_if_logged_in(self, api_client, db):
        user = UserFactory.create()
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "secret"}

        api_client.force_authenticate(user=user)
        response = api_client.delete(reverse("user-me"), data=data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username=user.username).exists()

    def test_not_delete_if_fails_password_validation(self, api_client, db):
        user = UserFactory.create()
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "incorrect"}

        api_client.force_authenticate(user=user)
        response = api_client.delete(reverse("user-me"), data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}

    def test_permission_class(self, api_client, db):
        old_value = djoser_settings.PERMISSIONS["user_delete"]
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"PERMISSIONS": {"user_delete": [PermCheckClass]}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            user = UserFactory.create()
            assert User.objects.filter(username=user.username).exists()
            data = {"current_password": "incorrect"}

            api_client.force_authenticate(user=user)
            api_client.delete(reverse("user-me"), data=data)
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"PERMISSIONS": {"user_delete": old_value}})
        ).enable()

    def test_serializer_class(self, api_client, db):
        old_value = djoser_settings.SERIALIZERS["user_delete"]
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"SERIALIZERS": {"user_delete": SerializerCheckClass}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            user = UserFactory.create()
            assert User.objects.filter(username=user.username).exists()
            data = {"current_password": "incorrect"}

            api_client.force_authenticate(user=user)
            api_client.delete(reverse("user-me"), data=data)
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"SERIALIZERS": {"user_delete": old_value}})
        ).enable()


class TestUserViewSetDeletion:
    def test_delete_user_if_logged_in(self, api_client, db):
        user = UserFactory.create()
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "secret"}
        api_client.force_authenticate(user=user)

        response = api_client.delete(
            reverse("user-detail", kwargs={User._meta.pk.name: user.pk}),
            data=data,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username=user.username).exists()

    def test_not_delete_if_fails_password_validation(self, api_client, db):
        user = UserFactory.create()
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "incorrect"}

        api_client.force_authenticate(user=user)

        response = api_client.delete(
            reverse("user-detail", kwargs={User._meta.pk.name: user.pk}),
            data=data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}

    def test_permission_class(self, api_client, db):
        old_value = djoser_settings.PERMISSIONS["user_delete"]
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"PERMISSIONS": {"user_delete": [PermCheckClass]}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            user = UserFactory.create()
            assert User.objects.filter(username=user.username).exists()
            data = {"current_password": "incorrect"}

            api_client.force_authenticate(user=user)
            api_client.delete(
                reverse("user-detail", kwargs={User._meta.pk.name: user.pk}),
                data=data,
            )
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"PERMISSIONS": {"user_delete": old_value}})
        ).enable()

    def test_serializer_class(self, api_client, db):
        old_value = djoser_settings.SERIALIZERS["user_delete"]
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"SERIALIZERS": {"user_delete": SerializerCheckClass}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            user = UserFactory.create()
            assert User.objects.filter(username=user.username).exists()
            data = {"current_password": "incorrect"}

            api_client.force_authenticate(user=user)
            api_client.delete(
                reverse("user-detail", kwargs={User._meta.pk.name: user.pk}),
                data=data,
            )
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"SERIALIZERS": {"user_delete": old_value}})
        ).enable()
