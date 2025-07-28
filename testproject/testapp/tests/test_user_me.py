import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.reverse import reverse

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSetMe:

    class DummyCurrentUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("is_staff",)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("user-me")

    def test_get_current_user_returns_user_data(self, authenticated_client):
        response = authenticated_client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == set(
            [User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS
        )

    def test_put_email_change_without_activation_email_requirement(
        self, authenticated_client, user, djoser_settings
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = False
        data = {"email": "ringo@beatles.com"}
        response = authenticated_client.put(self.base_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert data["email"] == user.email
        assert user.is_active

    def test_put_email_change_with_activation_email_requirement(
        self, authenticated_client, user, mailoutbox, djoser_settings
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = True
        data = {"email": "ringo@beatles.com"}
        response = authenticated_client.put(self.base_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert data["email"] == user.email
        assert not user.is_active
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [data["email"]]

    def test_patch_email_change_without_activation_email_requirement(
        self, authenticated_client, user, djoser_settings
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = False
        data = {"email": "ringo@beatles.com"}
        response = authenticated_client.patch(self.base_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert data["email"] == user.email
        assert user.is_active

    def test_patch_email_change_with_activation_email_requirement(
        self, authenticated_client, user, mailoutbox, djoser_settings
    ):
        djoser_settings["SEND_ACTIVATION_EMAIL"] = True
        data = {"email": "ringo@beatles.com"}
        response = authenticated_client.patch(self.base_url, data=data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert data["email"] == user.email
        assert not user.is_active
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [data["email"]]

    def test_current_user_serializer_configuration(
        self, djoser_settings, authenticated_client, user
    ):
        """Test that the endpoints use the proper serializer.

        How it works: it adds an additional field to the current_user
        serializer and then checks that the field shows in the response.
        """
        djoser_settings["SERIALIZERS"] = {
            "current_user": self.DummyCurrentUserSerializer
        }
        response = authenticated_client.get(self.base_url)

        user.refresh_from_db()
        assert response.data["is_staff"] == user.is_staff


@pytest.mark.django_db
class TestUserViewSetMeDelete:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = reverse("user-me")

    def test_delete_authenticated_user_with_correct_password(
        self, authenticated_client, user
    ):
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "secret"}

        response = authenticated_client.delete(self.base_url, data=data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username=user.username).exists()

    def test_delete_user_fails_with_incorrect_password(
        self, authenticated_client, user
    ):
        assert User.objects.filter(username=user.username).exists()
        data = {"current_password": "incorrect"}

        response = authenticated_client.delete(self.base_url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"current_password": ["Invalid password."]}
