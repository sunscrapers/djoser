import pytest
from django.conf import settings
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
class TestUserViewSetList:
    @pytest.fixture
    def url(self):
        return reverse("user-list")

    def test_unauthenticated_user_cannot_list_users(self, anonymous_api_client, url):
        response = anonymous_api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": True}))
    def test_user_cannot_list_other_users(self, api_client, user, superuser, url):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["username"] == user.username

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": False}))
    def test_user_can_list_other_users(self, api_client, user, superuser, url):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_superuser_can_list_all_users(self, api_client, user, superuser, url):
        api_client.force_authenticate(user=superuser)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
        api_client.force_authenticate(user=None)
