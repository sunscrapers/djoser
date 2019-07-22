from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .common import create_user

User = get_user_model()


class UserViewTest(
    APITestCase, assertions.EmailAssertionsMixin, assertions.StatusCodeAssertionsMixin
):
    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_get_return_user(self):
        response = self.client.get(self.url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            set([User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS),
        )

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_email_change_with_send_activation_email_false(self):
        data = {"email": "ringo@beatles.com"}

        response = self.client.put(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertTrue(self.user.is_active)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_email_change_with_send_activation_email_true(self):
        data = {"email": "ringo@beatles.com"}

        response = self.client.put(self.url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertFalse(self.user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data["email"]])

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": False}))
    def test_fail_403_without_permission(self):
        other_user = create_user(
            **{
                "username": "paul",
                "password": "verysecret",
                "email": "paul@beatles.com",
            }
        )
        data = {"email": "ringo@beatles.com"}
        url = reverse("user-detail", kwargs={"pk": other_user.pk})

        response = self.client.get(self.url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response2 = self.client.get(url)
        self.assert_status_equal(response2, status.HTTP_403_FORBIDDEN)
        response3 = self.client.put(url, data=data)
        self.assert_status_equal(response3, status.HTTP_403_FORBIDDEN)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"HIDE_USERS": True}))
    def test_fail_404_without_permission(self):
        other_user = create_user(
            **{
                "username": "paul",
                "password": "verysecret",
                "email": "paul@beatles.com",
            }
        )
        data = {"email": "ringo@beatles.com"}
        url = reverse("user-detail", kwargs={"pk": other_user.pk})

        response = self.client.get(self.url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        response2 = self.client.get(url)
        self.assert_status_equal(response2, status.HTTP_404_NOT_FOUND)
        response3 = self.client.put(url, data=data)
        self.assert_status_equal(response3, status.HTTP_404_NOT_FOUND)
