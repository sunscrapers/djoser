import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

User = get_user_model()


@pytest.fixture
def user_url(user):
    return reverse("user-detail", kwargs={User._meta.pk.name: user.pk})


@pytest.fixture
def other_user_url(other_user):
    return reverse("user-detail", kwargs={User._meta.pk.name: other_user.pk})


@pytest.mark.django_db
class TestUserView:
    def test_get_return_user(self, api_client, user, user_url):
        response = api_client.get(user_url)

        assert response.status_code == status.HTTP_200_OK
        expected_keys = {User.USERNAME_FIELD, User._meta.pk.name} | set(
            User.REQUIRED_FIELDS
        )
        assert set(response.data.keys()) == expected_keys

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_email_change_with_send_activation_email_false(
        self, api_client, user, user_url
    ):
        data = {"username": user.username, "email": "ringo@beatles.com"}

        response = api_client.put(user_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert user.is_active

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_email_change_with_send_activation_email_true(
        self, api_client, user, user_url
    ):
        data = {"username": user.username, "email": "ringo@beatles.com"}

        response = api_client.put(user_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == data["email"]
        assert not user.is_active
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [data["email"]]

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": False}))
    def test_fail_403_without_permission(self, api_client, user_url, other_user_url):
        data = {"email": "ringo@beatles.com"}

        response1 = api_client.put(other_user_url, data=data)
        assert response1.status_code == status.HTTP_403_FORBIDDEN

        response2 = api_client.get(user_url)
        assert response2.status_code == status.HTTP_200_OK

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": True}))
    def test_fail_404_without_permission(self, api_client, user_url, other_user_url):
        data = {"email": "ringo@beatles.com"}

        response1 = api_client.put(other_user_url, data=data)
        assert response1.status_code == status.HTTP_404_NOT_FOUND

        response2 = api_client.get(user_url)
        assert response2.status_code == status.HTTP_200_OK
