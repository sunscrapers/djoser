from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions, restframework, utils
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.views
from .common import create_user


class SetUsernameViewTest(restframework.APIViewTestCase,
                          assertions.EmailAssertionsMixin,
                          assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetUsernameView

    def test_post_set_new_username(self):
        user = create_user()
        data = {
            'new_username': 'ringo',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user = utils.refresh(user)
        self.assertEqual(data['new_username'], user.username)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SET_USERNAME_RETYPE': True})
    )
    def test_post_not_set_new_username_if_mismatch(self):
        user = create_user()
        data = {
            'new_username': 'ringo',
            're_new_username': 'wrong',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(data['new_username'], user.username)

    def test_post_not_set_new_username_if_exists(self):
        username = 'tom'
        create_user(username=username)
        user = create_user(username='john')
        data = {
            'new_username': username,
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(user.username, username)

    def test_post_not_set_new_username_if_invalid(self):
        user = create_user()
        data = {
            'new_username': '$ wrong username #',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(user.username, data['new_username'])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_post_update_username_and_send_activation_email(self):
        user = create_user()
        data = {
            'new_username': 'dango',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])

        user = get_user_model().objects.get(username='dango')
        self.assertFalse(user.is_active)

    def test_post_not_set_new_username_if_same(self):
        user = create_user()
        data = {
            'new_username': 'john',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(user.is_active)


class UserViewSetChangeUsernameTest(APITestCase,
                                    assertions.EmailAssertionsMixin,
                                    assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetUsernameView

    def setUp(self):
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_post_set_new_username(self):
        data = {
            'new_username': 'ringo',
            'current_password': 'secret',
        }

        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.user = utils.refresh(self.user)
        self.assertEqual(data['new_username'], self.user.username)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SET_USERNAME_RETYPE': True})
    )
    def test_post_not_set_new_username_if_mismatch(self):
        data = {
            'new_username': 'ringo',
            're_new_username': 'wrong',
            'current_password': 'secret',
        }
        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(self.user)
        self.assertNotEqual(data['new_username'], user.username)

    def test_post_not_set_new_username_if_exists(self):
        username = 'tom'
        create_user(username=username)
        user = create_user(username='ringo')
        self.client.force_authenticate(user=user)

        data = {
            'new_username': username,
            'current_password': 'secret',
        }
        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(user.username, username)

    def test_post_not_set_new_username_if_invalid(self):
        data = {
            'new_username': '$ wrong username #',
            'current_password': 'secret',
        }
        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.user = utils.refresh(self.user)
        self.assertNotEqual(self.user.username, data['new_username'])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_post_update_username_and_send_activation_email(self):
        data = {
            'new_username': 'dango',
            'current_password': 'secret',
        }
        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[self.user.email])

        user = get_user_model().objects.get(username='dango')
        self.assertFalse(user.is_active)

    def test_post_not_set_new_username_if_same(self):
        data = {
            'new_username': 'john',
            'current_password': 'secret',
        }
        response = self.client.post(reverse('user-change-username'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user.is_active)
