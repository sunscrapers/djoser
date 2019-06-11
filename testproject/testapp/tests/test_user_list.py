from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .common import create_user


class UserViewSetListTest(APITestCase, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        self.user = create_user(username="user", email="user@example.com")
        self.superuser = create_user(
            username="superuser", email="superuser@example.com", is_superuser=True
        )

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(reverse("user-list"))

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_list_other_users(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("user-list"))

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_superuser_can_list_all_users(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse("user-list"))

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
