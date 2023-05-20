from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user, login_user

import djoser.permissions
import djoser.views


class BaseUserViewSetListTest(APITestCase, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super().setUp()
        self.user = create_user(username="user", email="user@example.com")
        self.superuser = create_user(
            username="superuser",
            email="superuser@example.com",
            is_superuser=True,
            is_staff=True,
        )


class ModifiedPermissionsTest(APITestCase):
    """Test case that overrides user-detail permission to
    CurrentUserOrAdminOrReadOnly."""

    def setUp(self):
        super().setUp()
        self.previous_permissions = djoser.views.UserViewSet.permission_classes
        djoser.views.UserViewSet.permission_classes = [
            djoser.permissions.CurrentUserOrAdminOrReadOnly
        ]

    def tearDown(self):
        super().tearDown()
        djoser.views.UserViewSet.permission_classes = self.previous_permissions


class UserViewSetListTest(BaseUserViewSetListTest):
    def test_unauthenticated_user_cannot_get_user_detail(self):
        response = self.client.get(reverse("user-detail", args=[self.user.pk]))

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_get_own_details(self):
        login_user(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[self.user.pk]))

        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_user_cannot_get_other_user_detail(self):
        login_user(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[self.superuser.pk]))

        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

    def test_superuser_can_get_other_user_detail(self):
        login_user(self.client, self.superuser)
        response = self.client.get(reverse("user-detail", args=[self.user.pk]))

        self.assert_status_equal(response, status.HTTP_200_OK)


class ModifiedPermissionsUserViewSetListTest(
    BaseUserViewSetListTest,
    ModifiedPermissionsTest,
):
    def test_user_can_get_other_user_detail(self):
        login_user(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[self.superuser.pk]))
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_user_cant_set_other_user_detail(self):
        login_user(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[self.superuser.pk]))
        self.assert_status_equal(response, status.HTTP_200_OK)


class UserViewSetEditTest(APITestCase, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_patch_edits_user_attribute(self):
        user = create_user()
        djoser.signals.user_updated.connect(self.signal_receiver)
        login_user(self.client, user)
        response = self.client.patch(
            path=reverse("user-detail", args=(user.pk,)),
            data={"email": "new@gmail.com"},
        )

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue("email" in response.data)

        user.refresh_from_db()
        self.assertTrue(user.email == "new@gmail.com")
        self.assertTrue(self.signal_sent)

    def test_patch_cant_edit_others_attribute(self):
        user = create_user()
        another_user = create_user(
            **{"username": "paul", "password": "secret", "email": "paul@beatles.com"}
        )
        login_user(self.client, user)
        response = self.client.patch(
            path=reverse("user-detail", args=(another_user.pk,)),
            data={"email": "new@gmail.com"},
        )

        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

        another_user.refresh_from_db()
        self.assertTrue(another_user.email == "paul@beatles.com")

    def test_put_edits_user_attribute(self):
        user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        user = create_user(**user_data)
        user_data["password"] = "changed_secret"
        login_user(self.client, user)

        response = self.client.patch(
            path=reverse("user-detail", args=(user.pk,)), data=user_data
        )

        self.assert_status_equal(response, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.email == "paul@beatles.com")

    def test_put_cant_edit_others_attribute(self):
        user = create_user()
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = create_user(**another_user_data)
        another_user_data["password"] = "changed_secret"
        login_user(self.client, user)

        response = self.client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

        another_user.refresh_from_db()
        self.assertTrue(another_user.email == "paul@beatles.com")


class ModifiedPermissionsViewSetEditTest(
    ModifiedPermissionsTest, assertions.StatusCodeAssertionsMixin
):
    def test_put_cant_edit_others_attribute(self):
        user = create_user()
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = create_user(**another_user_data)
        another_user_data["password"] = "changed_secret"
        another_user_data["email"] = "paulmc@beatles.com"
        login_user(self.client, user)

        response = self.client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

        another_user.refresh_from_db()
        assert another_user.email, "paul@beatles.com"

    def test_put_cant_edit_own_attribute(self):
        user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        user = create_user(**user_data)
        user_data["password"] = "changed_secret"
        user_data["email"] = "paulmc@beatles.com"
        login_user(self.client, user)

        response = self.client.patch(
            path=reverse("user-detail", args=(user.pk,)), data=user_data
        )

        self.assert_status_equal(response, status.HTTP_200_OK)

        user.refresh_from_db()
        assert user.email, "paulmc@beatles.com"

    def test_superuser_put_can_edit_others_attribute(self):
        superuser = create_user(
            is_superuser=True,
            is_staff=True,
        )
        another_user_data = {
            "username": "paul",
            "password": "secret",
            "email": "paul@beatles.com",
        }
        another_user = create_user(**another_user_data)
        another_user_data["password"] = "changed_secret"
        another_user_data["email"] = "paulmc@beatles.com"
        login_user(self.client, superuser)

        response = self.client.patch(
            path=reverse("user-detail", args=(another_user.pk,)), data=another_user_data
        )

        self.assert_status_equal(response, status.HTTP_200_OK)

        another_user.refresh_from_db()
        assert another_user.email == "paulmc@beatles.com"
