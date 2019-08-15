from django.conf import settings
from django.test import override_settings
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
            username="superuser",
            email="superuser@example.com",
            is_superuser=True,
            is_staff=True,
        )

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": True}))
    def test_user_cannot_list_other_users(self):
        login_user(self.client, self.user)
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": False}))
    def test_user_can_list_other_users(self):
        login_user(self.client, self.user)
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_superuser_can_list_all_users(self):
        login_user(self.client, self.superuser)
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
