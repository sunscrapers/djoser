import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from djet import assertions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.views
from djoser.conf import settings as djoser_settings

from .common import PermCheckClass, RunCheck, SerializerCheckClass, create_user

User = get_user_model()


class UserMeDeleteViewTest(
    APITestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
    assertions.InstanceAssertionsMixin,
):
    viewset = djoser.views.UserViewSet

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

    def test_permission_class(self):
        old_value = djoser_settings.PERMISSIONS["user_delete"]
        with override_settings(
            DJOSER=dict(
                settings.DJOSER, **{"PERMISSIONS": {"user_delete": [PermCheckClass]}}
            )
        ), pytest.raises(RunCheck):
            user = create_user()
            self.assert_instance_exists(User, username="john")
            data = {"current_password": "incorrect"}

            self.client.force_authenticate(user=user)
            self.client.delete(reverse("user-me"), data=data, user=user)
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"PERMISSIONS": {"user_delete": old_value}})
        ).enable()

    def test_serializer_class(self):
        old_value = djoser_settings.SERIALIZERS["user_delete"]
        with override_settings(
            DJOSER=dict(
                settings.DJOSER,
                **{"SERIALIZERS": {"user_delete": SerializerCheckClass}},
            )
        ), pytest.raises(RunCheck):
            user = create_user()
            self.assert_instance_exists(User, username="john")
            data = {"current_password": "incorrect"}

            self.client.force_authenticate(user=user)
            self.client.delete(reverse("user-me"), data=data, user=user)
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"SERIALIZERS": {"user_delete": old_value}})
        ).enable()


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

        response = self.client.delete(
            reverse("user-detail", kwargs={"pk": user.pk}), data=data, user=user
        )

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(User, username="john")

    def test_not_delete_if_fails_password_validation(self):
        user = create_user()
        self.assert_instance_exists(User, username="john")
        data = {"current_password": "incorrect"}

        self.client.force_authenticate(user=user)

        response = self.client.delete(
            reverse("user-detail", kwargs={"pk": user.pk}), data=data, user=user
        )

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"current_password": ["Invalid password."]})

    def test_permission_class(self):
        old_value = djoser_settings.PERMISSIONS["user_delete"]
        with override_settings(
            DJOSER=dict(
                settings.DJOSER, **{"PERMISSIONS": {"user_delete": [PermCheckClass]}}
            )
        ), pytest.raises(RunCheck):
            user = create_user()
            self.assert_instance_exists(User, username="john")
            data = {"current_password": "incorrect"}

            self.client.force_authenticate(user=user)
            self.client.delete(
                reverse("user-detail", kwargs={"pk": user.pk}), data=data, user=user
            )
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"PERMISSIONS": {"user_delete": old_value}})
        ).enable()

    def test_serializer_class(self):
        old_value = djoser_settings.SERIALIZERS["user_delete"]
        with override_settings(
            DJOSER=dict(
                settings.DJOSER,
                **{"SERIALIZERS": {"user_delete": SerializerCheckClass}},
            )
        ), pytest.raises(RunCheck):
            user = create_user()
            self.assert_instance_exists(User, username="john")
            data = {"current_password": "incorrect"}

            self.client.force_authenticate(user=user)
            self.client.delete(
                reverse("user-detail", kwargs={"pk": user.pk}), data=data, user=user
            )
        override_settings(
            DJOSER=dict(settings.DJOSER, **{"SERIALIZERS": {"user_delete": old_value}})
        ).enable()
