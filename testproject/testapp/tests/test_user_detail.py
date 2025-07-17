import pytest
from rest_framework import status
from rest_framework.reverse import reverse

# Remove create_user import if only used in fixtures
# from testapp.tests.common import create_user

import djoser.permissions
import djoser.signals
import djoser.views

# Assume user and superuser fixtures are defined globally (e.g., in conftest.py)
# Define another_user fixture locally if not global


@pytest.fixture
def modified_permissions(monkeypatch):
    """Fixture that overrides user-detail permission to
    CurrentUserOrAdminOrReadOnly."""
    monkeypatch.setattr(
        djoser.views.UserViewSet,
        "permission_classes",
        [djoser.permissions.CurrentUserOrAdminOrReadOnly],
    )
    yield


@pytest.mark.django_db
class TestUserViewSetList:
    # Removed setUp method, replaced by fixtures user and superuser

    def test_unauthenticated_user_cannot_get_user_detail(
        self, anonymous_api_client, user
    ):
        response = anonymous_api_client.get(reverse("user-detail", args=[user.pk]))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_get_own_details(self, api_client, user):
        response = api_client.get(reverse("user-detail", args=[user.pk]))
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_get_other_user_detail(self, api_client, user, superuser):
        response = api_client.get(reverse("user-detail", args=[superuser.pk]))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_superuser_can_get_other_user_detail(self, api_client, superuser, user):
        api_client.force_authenticate(user=superuser)
        response = api_client.get(reverse("user-detail", args=[user.pk]))
        assert response.status_code == status.HTTP_200_OK
        api_client.force_authenticate(user=None)


@pytest.mark.django_db
@pytest.mark.usefixtures("modified_permissions")
class TestModifiedPermissionsUserViewSetList:
    def test_user_can_get_other_user_detail(self, api_client, user, superuser):
        response = api_client.get(reverse("user-detail", args=[superuser.pk]))
        assert response.status_code == status.HTTP_200_OK

    def test_user_cant_patch_other_user_detail(self, api_client, user, superuser):
        response = api_client.patch(
            reverse("user-detail", args=[superuser.pk]), data={}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserViewSetEdit:
    @pytest.fixture(autouse=True)
    def setup_signal(self):
        self.signal_sent = False
        djoser.signals.user_updated.connect(self._signal_receiver)
        yield
        djoser.signals.user_updated.disconnect(self._signal_receiver)

    def _signal_receiver(self, sender, **kwargs):
        self.signal_sent = True

    def test_patch_edits_user_attribute(self, api_client, user):
        response = api_client.patch(
            path=reverse("user-detail", args=(user.pk,)),
            data={"email": "new@gmail.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "email" in response.data

        user.refresh_from_db()
        assert user.email == "new@gmail.com"
        assert self.signal_sent

    def test_patch_cant_edit_others_attribute(self, api_client, user, other_user):
        response = api_client.patch(
            path=reverse("user-detail", args=(other_user.pk,)),
            data={"email": "new@gmail.com"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        other_user.refresh_from_db()
        assert other_user.email == "paul@beatles.com"

    def test_put_edits_user_attribute(self, api_client, user):
        update_data = {
            "username": user.username,
            "email": "paulmc@beatles.com",
        }
        response = api_client.put(
            path=reverse("user-detail", args=(user.pk,)), data=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "paulmc@beatles.com"

        user.refresh_from_db()
        assert user.email == "paulmc@beatles.com"

    def test_put_cant_edit_others_attribute(self, api_client, user, other_user):
        update_data = {
            "username": other_user.username,
            "email": "paulmc@beatles.com",
        }
        response = api_client.put(
            path=reverse("user-detail", args=(other_user.pk,)), data=update_data
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        other_user.refresh_from_db()
        assert other_user.email == "paul@beatles.com"


@pytest.mark.django_db
@pytest.mark.usefixtures("modified_permissions")
class TestModifiedPermissionsViewSetEdit:
    def test_patch_cant_edit_others_attribute(self, api_client, user, superuser):
        update_data = {"email": "paulmc@beatles.com"}
        response = api_client.patch(
            path=reverse("user-detail", args=(superuser.pk,)), data=update_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        superuser.refresh_from_db()
        assert superuser.email != "paulmc@beatles.com"

    def test_patch_can_edit_own_attribute(self, api_client, user):
        update_data = {"email": "paulmc@beatles.com"}
        response = api_client.patch(
            path=reverse("user-detail", args=(user.pk,)), data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == "paulmc@beatles.com"

    def test_superuser_patch_can_edit_others_attribute(
        self, api_client, superuser, other_user
    ):
        update_data = {"email": "paulmc@beatles.com"}
        api_client.force_authenticate(user=superuser)
        response = api_client.patch(
            path=reverse("user-detail", args=(other_user.pk,)), data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        other_user.refresh_from_db()
        assert other_user.email == "paulmc@beatles.com"
        api_client.force_authenticate(user=None)
