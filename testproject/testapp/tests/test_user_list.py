from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from testapp.tests.common import create_user, login_user


class UserViewSetListTest(APITestCase, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        self.base_url = reverse("user-list")
        self.user = create_user(username="user", email="user@example.com")
        self.superuser = create_user(
            username="superuser", email="superuser@example.com", is_superuser=True
        )

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_list_other_users(self):
        login_user(self.client, self.user)
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_superuser_can_list_all_users(self):
        login_user(self.client, self.superuser)
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
