from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions, restframework
from rest_framework import status
import djoser.constants
import djoser.utils
import djoser.views

from .common import create_user, mock, perform_create_mock

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
        self.assertEqual(
            response.data,
            {'password': ['Password 666 is not allowed.']}
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
