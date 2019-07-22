import djoser.views
from django.contrib.auth import get_user_model
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .common import create_user

User = get_user_model()


class UserDeleteViewTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    viewset = djoser.views.UserViewSet

    # view_class = djoser.views.UserDeleteView

    def test_delete_user_if_logged_in(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "secret"}

        self.client.force_authenticate(user=user)
        response = self.client.delete(reverse("user-me"), data=data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(User, username="john")

    def test_not_delete_if_fails_password_validation(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "incorrect"}

        self.client.force_authenticate(user=user)
        response = self.client.delete(reverse("user-me"), data=data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"current_password": ["Invalid password."]})


class UserViewSetDeletionTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    def test_delete_user_if_logged_in(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "secret"}
        self.client.force_authenticate(user=user)

        response = self.client.delete(reverse("user-me"), data=data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(User, username="john")

    def test_not_delete_if_fails_password_validation(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "incorrect"}

        self.client.force_authenticate(user=user)

        response = self.client.delete(reverse("user-me"), data=data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"current_password": ["Invalid password."]})
