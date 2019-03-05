from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions, restframework
from rest_framework import __version__ as drf_version
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.constants
import djoser.utils
import djoser.views
from .common import create_user, mock, perform_create_mock
from pkg_resources import parse_version

User = get_user_model()


class UserCreateViewTest(restframework.APIViewTestCase,
                         assertions.StatusCodeAssertionsMixin,
                         assertions.EmailAssertionsMixin,
                         assertions.InstanceAssertionsMixin):
    view_class = djoser.views.UserCreateView

    def test_post_create_user_without_login(self):
        data = {
            'username': 'john',
            'password': 'secret',
            'csrftoken': 'asdf',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue('password' not in response.data)
        self.assert_instance_exists(User, username=data['username'])
        user = User.objects.get(username=data['username'])
        self.assertTrue(user.check_password(data['password']))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_post_create_user_with_login_and_send_activation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }
        request = self.factory.post(data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = User.objects.get(username='john')
        self.assertFalse(user.is_active)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
            'SEND_ACTIVATION_EMAIL': False, 'SEND_CONFIRMATION_EMAIL': True
        })
    )
    def test_post_create_user_with_login_and_send_confirmation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }
        request = self.factory.post(data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = User.objects.get(username='john')
        self.assertTrue(user.is_active)

    def test_post_not_create_new_user_if_username_exists(self):
        create_user(username='john')
        data = {
            'username': 'john',
            'password': 'secret',
            'csrftoken': 'asdf',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_not_register_if_fails_password_validation(self):
        data = {
            'username': 'john',
            'password': '666',
            'csrftoken': 'asdf',
        }

        request = self.factory.post(data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        response.render()
        self.assertEqual(
            str(response.data['password'][0]),
            'Password 666 is not allowed.',
        )
        if parse_version(drf_version) >= parse_version('3.9.0'):
            self.assertEqual(
                response.data['password'][0].code,
                'no666',
            )

    @mock.patch(
        'djoser.serializers.UserCreateSerializer.perform_create',
        side_effect=perform_create_mock
    )
    def test_post_return_400_for_integrity_error(self, perform_create):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }

        request = self.factory.post(data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, [djoser.constants.CANNOT_CREATE_USER_ERROR]
        )


class UserViewSetCreationTest(APITestCase,
                              assertions.StatusCodeAssertionsMixin,
                              assertions.EmailAssertionsMixin,
                              assertions.InstanceAssertionsMixin):

    def test_post_create_user_without_login(self):
        data = {
            'username': 'john',
            'password': 'secret',
        }

        response = self.client.post(path=reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue('password' not in response.data)

        self.assert_instance_exists(User, username=data['username'])
        user = User.objects.get(username=data['username'])
        self.assertTrue(user.check_password(data['password']))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_post_create_user_with_login_and_send_activation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }

        response = self.client.post(reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = User.objects.get(username='john')
        self.assertFalse(user.is_active)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{
            'SEND_ACTIVATION_EMAIL': False, 'SEND_CONFIRMATION_EMAIL': True
        })
    )
    def test_post_create_user_with_login_and_send_confirmation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }
        response = self.client.post(reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(User, username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = User.objects.get(username='john')
        self.assertTrue(user.is_active)

    def test_post_not_create_new_user_if_username_exists(self):
        create_user(username='john')
        data = {
            'username': 'john',
            'password': 'secret',
            'csrftoken': 'asdf',
        }
        response = self.client.post(reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_not_register_if_fails_password_validation(self):
        data = {
            'username': 'john',
            'password': '666',
            'csrftoken': 'asdf',
        }

        response = self.client.post(reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['password'][0]),
            'Password 666 is not allowed.',
        )
        if parse_version(drf_version) >= parse_version('3.9.0'):
            self.assertEqual(
                response.data['password'][0].code,
                'no666',
            )

    @mock.patch(
        'djoser.serializers.UserCreateSerializer.perform_create',
        side_effect=perform_create_mock
    )
    def test_post_return_400_for_integrity_error(self, perform_create):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }

        response = self.client.post(reverse('user-list'), data=data)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, [djoser.constants.CANNOT_CREATE_USER_ERROR]
        )


class UserViewSetEditTest(APITestCase,
                          assertions.StatusCodeAssertionsMixin):

    def test_patch_edits_user_attribute(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            path=reverse('user-detail', args=(user.pk,)),
            data={'email': 'new@gmail.com'}
        )

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue('email' in response.data)

        user.refresh_from_db()
        self.assertTrue(user.email == 'new@gmail.com')

    def test_patch_cant_edit_others_attribute(self):
        user = create_user()
        another_user = create_user(**{
            'username': 'paul',
            'password': 'secret',
            'email': 'paul@beatles.com',
        })
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            path=reverse('user-detail', args=(another_user.pk,)),
            data={'email': 'new@gmail.com'}
        )

        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)

        another_user.refresh_from_db()
        self.assertTrue(another_user.email == 'paul@beatles.com')


class TestResendActivationEmail(
    restframework.APIViewTestCase,
    assertions.StatusCodeAssertionsMixin,
    assertions.EmailAssertionsMixin,
):
    view_class = djoser.views.ResendActivationView

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_resend_activation_view(self):
        user = create_user(is_active=False)
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)
        self.view(request)
        self.assert_email_exists(to=[user.email])

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': False})
    )
    def test_dont_resend_activation_when_disabled(self):
        user = create_user(is_active=False)
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)
        self.view(request)
        self.assert_emails_in_mailbox(0)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_dont_resend_activation_when_active(self):
        user = create_user(is_active=True)
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)
        self.view(request)
        self.assert_emails_in_mailbox(0)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True})
    )
    def test_dont_resend_activation_when_no_password(self):
        user = create_user(is_active=False, password=None)
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)
        self.view(request)
        self.assert_emails_in_mailbox(0)
