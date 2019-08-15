from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions
from rest_framework import serializers, status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from testapp.tests.common import create_user, login_user

User = get_user_model()


class UserViewSetMeTest(
    APITestCase,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin,
    assertions.StatusCodeAssertionsMixin,
):
    class DummyCurrentUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("is_staff",)

    def setUp(self):
        self.base_url = reverse("user-me")
        self.user = create_user()
        login_user(self.client, self.user)

    def test_get_return_user(self):
        response = self.client.get(self.base_url)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            set([User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS),
        )

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_put_email_change_with_send_activation_email_false(self):
        data = {"email": "ringo@beatles.com"}
        response = self.client.put(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertTrue(self.user.is_active)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_put_email_change_with_send_activation_email_true(self):
        data = {"email": "ringo@beatles.com"}
        response = self.client.put(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertFalse(self.user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data["email"]])

    def test_patch_email_change_with_send_activation_email_false(self):
        data = {"email": "ringo@beatles.com"}
        response = self.client.patch(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertTrue(self.user.is_active)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_patch_email_change_with_send_activation_email_true(self):
        data = {"email": "ringo@beatles.com"}
        response = self.client.patch(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(data["email"], self.user.email)
        self.assertFalse(self.user.is_active)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data["email"]])

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{"SERIALIZERS": {"current_user": DummyCurrentUserSerializer}},
        )
    )
    def test_serializer(self):
        """
        Test that the endpoints use the proper serializer.

        How it works: it adds an additional field to the current_user
        serializer and then checks that the field shows in the response.
        """
        response = self.client.get(self.base_url)

        self.user.refresh_from_db()
        self.assertEqual(response.data["is_staff"], self.user.is_staff)


class UserViewSetMeDeleteTest(
    APITestCase,
    assertions.InstanceAssertionsMixin,
    assertions.StatusCodeAssertionsMixin,
):
    def setUp(self):
        self.base_url = reverse("user-me")

    def test_delete_user_if_logged_in(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "secret"}
        login_user(self.client, user)

        response = self.client.delete(self.base_url, data=data, user=user)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(User, username="john")

    def test_not_delete_if_fails_password_validation(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "incorrect"}
        login_user(self.client, user)

        response = self.client.delete(self.base_url, data=data, user=user)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"current_password": ["Invalid password."]})
