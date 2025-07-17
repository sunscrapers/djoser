import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from rest_framework import serializers, status
from rest_framework.reverse import reverse

User = get_user_model()


class DummyCurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_staff",)


@pytest.fixture
def url():
    return reverse("user-me")


@pytest.mark.django_db
class TestUserViewSetMe:
    def test_get_return_user(self, api_client, user, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        expected_keys = {User.USERNAME_FIELD, User._meta.pk.name} | set(
            User.REQUIRED_FIELDS
        )
        assert set(response.data.keys()) == expected_keys

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_put_email_change_with_send_activation_email_false(
        self, api_client, user, url
    ):
        data = {"email": "ringo@beatles.com"}
        response = api_client.put(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert user.is_active

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_put_email_change_with_send_activation_email_true(
        self, api_client, user, url
    ):
        data = {"email": "ringo@beatles.com"}
        response = api_client.put(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert not user.is_active
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data["email"]]

    def test_patch_email_change_with_send_activation_email_false(
        self, api_client, user, url
    ):
        data = {"email": "ringo@beatles.com"}
        response = api_client.patch(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert user.is_active

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_patch_email_change_with_send_activation_email_true(
        self, api_client, user, url
    ):
        data = {"email": "ringo@beatles.com"}
        response = api_client.patch(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert not user.is_active
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data["email"]]

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{
                "SERIALIZERS": {
                    "current_user": f"{__name__}.DummyCurrentUserSerializer"
                }
            },
        )
    )
    def test_serializer(self, api_client, user, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert "is_staff" in response.data
        assert response.data["is_staff"] == user.is_staff


@pytest.mark.django_db
class TestUserViewSetMeDelete:
    def test_delete_user_if_logged_in(self, api_client, user, url):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "secret"}
        response = api_client.delete(url, data=data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username="john").exists()

    def test_not_delete_if_fails_password_validation(self, api_client, user, url):
        assert User.objects.filter(username="john").exists()
        data = {"current_password": "incorrect"}
        response = api_client.delete(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}
        assert User.objects.filter(username="john").exists()
