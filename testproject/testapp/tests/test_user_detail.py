from testapp.factories import UserFactory
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

import djoser.permissions
import djoser.views
import djoser.signals


@pytest.fixture
def setup_modified_permissions():
    """
    Test case that overrides user-detail permission to CurrentUserOrAdminOrReadOnly.
    """
    previous_permissions = djoser.views.UserRetrieveView.permission_classes
    djoser.views.UserRetrieveView.permission_classes = [
        djoser.permissions.CurrentUserOrAdminOrReadOnly
    ]
    # Also update the UpdateView permissions since
    # they're part of the same functionality
    previous_update_permissions = djoser.views.UserUpdateView.permission_classes
    djoser.views.UserUpdateView.permission_classes = [
        djoser.permissions.CurrentUserOrAdminOrReadOnly
    ]
    yield
    djoser.views.UserRetrieveView.permission_classes = previous_permissions
    djoser.views.UserUpdateView.permission_classes = previous_update_permissions


@pytest.mark.django_db
class TestUserRetrieveView:
    @pytest.fixture(autouse=True)
    def setup(self, user, create_superuser):
        self.user = user
        self.superuser = create_superuser

    def test_unauthenticated_user_cannot_get_user_detail(self, api_client):
        response = api_client.get(reverse("user-detail", args=[self.user.pk]))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_get_own_details(self, authenticated_client):
        response = authenticated_client.get(reverse("user-detail", args=[self.user.pk]))

        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_get_other_user_detail(self, authenticated_client):
        response = authenticated_client.get(
            reverse("user-detail", args=[self.superuser.pk])
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_superuser_can_get_other_user_detail(self, api_client):
        # Login as superuser
        api_client.force_authenticate(user=self.superuser)
        response = api_client.get(reverse("user-detail", args=[self.user.pk]))

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestModifiedPermissionsUserRetrieveView:
    @pytest.fixture(autouse=True)
    def setup(self, user, create_superuser):
        self.user = user
        self.superuser = create_superuser

    def test_user_can_get_other_user_detail(
        self, api_client, setup_modified_permissions
    ):
        api_client.force_authenticate(user=self.user)
        response = api_client.get(reverse("user-detail", args=[self.superuser.pk]))
        assert response.status_code == status.HTTP_200_OK

    def test_user_cant_set_other_user_detail(
        self, api_client, setup_modified_permissions
    ):
        api_client.force_authenticate(user=self.user)
        response = api_client.get(reverse("user-detail", args=[self.superuser.pk]))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, user):
        self.user = user
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_patch_edits_user_attribute(self, api_client):
        djoser.signals.user_updated.connect(self.signal_receiver)
        api_client.force_authenticate(user=self.user)
        response = api_client.patch(
            path=reverse("user-detail", args=(self.user.pk,)),
            data={"email": "new@gmail.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "email" in response.data

        self.user.refresh_from_db()
        assert self.user.email == "new@gmail.com"
        assert self.signal_sent

    def test_patch_cant_edit_others_attribute(self, api_client, db):
        another_user = UserFactory.create(
            **{"username": "paul", "password": "secret", "email": "paul@beatles.com"}
        )
        api_client.force_authenticate(user=self.user)
        response = api_client.patch(
            path=reverse("user-detail", args=(another_user.pk,)),
            data={"email": "new@gmail.com"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        another_user.refresh_from_db()
        assert another_user.email == "paul@beatles.com"

    def test_put_edits_user_attribute(self, api_client):
        user_data = {
            "username": self.user.username,
            "password": "changed_secret",
            "email": self.user.email,
        }
        api_client.force_authenticate(user=self.user)

        response = api_client.patch(
            path=reverse("user-detail", args=(self.user.pk,)), data=user_data
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()
        assert self.user.email == user_data["email"]

    def test_put_cant_edit_others_attribute(self, api_client, db):
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = UserFactory.create(**another_user_data)
        another_user_data["password"] = "changed_secret"
        api_client.force_authenticate(user=self.user)

        response = api_client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        another_user.refresh_from_db()
        assert another_user.email == "paul@beatles.com"


@pytest.mark.django_db
class TestModifiedPermissionsViewSetEdit:
    @pytest.fixture(autouse=True)
    def setup(self, user, create_superuser):
        self.user = user
        self.create_user = UserFactory.create
        self.superuser = create_superuser

    def test_put_cant_edit_others_attribute(
        self, api_client, setup_modified_permissions
    ):
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = self.create_user(**another_user_data)
        another_user_data["password"] = "changed_secret"
        another_user_data["email"] = "paulmc@beatles.com"
        api_client.force_authenticate(user=self.user)

        response = api_client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        another_user.refresh_from_db()
        assert another_user.email == "paul@beatles.com"

    def test_put_cant_edit_own_attribute(self, api_client, setup_modified_permissions):
        user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        user = self.create_user(**user_data)
        user_data["password"] = "changed_secret"
        user_data["email"] = "paulmc@beatles.com"
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            path=reverse("user-detail", args=(user.pk,)), data=user_data
        )

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.email == "paulmc@beatles.com"

    def test_superuser_put_can_edit_others_attribute(
        self, api_client, setup_modified_permissions
    ):
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = self.create_user(**another_user_data)
        another_user_data["password"] = "changed_secret"
        another_user_data["email"] = "paulmc@beatles.com"
        api_client.force_authenticate(user=self.superuser)

        response = api_client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        assert response.status_code == status.HTTP_200_OK

        another_user.refresh_from_db()
        assert another_user.email == "paulmc@beatles.com"
