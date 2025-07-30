import pytest
from rest_framework import status
from rest_framework.reverse import reverse


class TestUserListView:
    @pytest.fixture(autouse=True)
    def setup(self, user, create_superuser):
        self.base_url = reverse("user-list")
        self.user = user
        self.superuser = create_superuser

    def test_unauthenticated_user_cannot_list_users(self, api_client):
        response = api_client.get(self.base_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_list_other_users(self, authenticated_client, djoser_settings):
        djoser_settings["HIDE_USERS"] = True
        response = authenticated_client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_user_can_list_other_users(self, authenticated_client, djoser_settings):
        djoser_settings["HIDE_USERS"] = False
        response = authenticated_client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_superuser_can_list_all_users(self, api_client):
        api_client.force_authenticate(user=self.superuser)
        response = api_client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
