import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse


User = get_user_model()


class SerializerCheckClass:
    def __init__(self, *args, **kwargs):
        raise RunCheck("working")


class RunCheck(Exception):
    pass


class PermCheckClass:
    def has_permission(self, *args, **kwargs):
        raise RunCheck("working")

    def has_object_permission(self, *args, **kwargs):
        raise RunCheck("working")


@pytest.mark.django_db
class TestUserMeDeleteView:
    def test_delete_user_if_logged_in(self, api_client, user):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "secret"}
        response = api_client.delete(reverse("user-me"), data=data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username="john").exists()

    def test_not_delete_if_fails_password_validation(self, api_client, user):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "incorrect"}
        response = api_client.delete(reverse("user-me"), data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}
        assert User.objects.filter(username="john").exists()

    def test_permission_class(self, api_client, user):
        perm_check_class_path = f"{PermCheckClass.__module__}.{PermCheckClass.__name__}"
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"PERMISSIONS": {"user_delete": [perm_check_class_path]}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            assert User.objects.filter(username="john").exists()
            data = {"current_password": "secret"}
            api_client.delete(reverse("user-me"), data=data)

    def test_serializer_class(self, api_client, user):
        serializer_check_class_path = (
            f"{SerializerCheckClass.__module__}.{SerializerCheckClass.__name__}"
        )
        with (
            override_settings(
                DJOSER=dict(
                    settings.DJOSER,
                    **{"SERIALIZERS": {"user_delete": serializer_check_class_path}},
                )
            ),
            pytest.raises(RunCheck),
        ):
            assert User.objects.filter(username="john").exists()
            data = {"current_password": "secret"}
            api_client.delete(reverse("user-me"), data=data)


@pytest.mark.django_db
class TestUserViewSetDeletion:
    def test_delete_user_if_logged_in(self, api_client, user):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "secret"}
        url = reverse("user-detail", kwargs={User._meta.pk.name: user.pk})
        response = api_client.delete(url, data=data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username="john").exists()

    def test_not_delete_if_fails_password_validation(self, api_client, user):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "incorrect"}
        url = reverse("user-detail", kwargs={User._meta.pk.name: user.pk})
        response = api_client.delete(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}
        assert User.objects.filter(username="john").exists()

    def test_permission_class(self, api_client, user, other_user):
        perm_check_class_path = f"{PermCheckClass.__module__}.{PermCheckClass.__name__}"
        data = {"current_password": "secret"}
        url_other = reverse("user-detail", kwargs={User._meta.pk.name: other_user.pk})

        with override_settings(
            DJOSER=dict(
                settings.DJOSER,
                **{"PERMISSIONS": {"user_delete": [perm_check_class_path]}},
            )
        ):
            response = api_client.delete(url_other, data=data)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_serializer_class(self, api_client, user, other_user):
        serializer_check_class_path = (
            f"{SerializerCheckClass.__module__}.{SerializerCheckClass.__name__}"
        )
        data = {"current_password": "secret"}
        url_other = reverse("user-detail", kwargs={User._meta.pk.name: other_user.pk})

        with override_settings(
            DJOSER=dict(
                settings.DJOSER,
                **{"SERIALIZERS": {"user_delete": serializer_check_class_path}},
            )
        ):
            response = api_client.delete(url_other, data=data)
            assert response.status_code == status.HTTP_403_FORBIDDEN
