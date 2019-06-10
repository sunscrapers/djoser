from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test.utils import override_settings
from djet import assertions, restframework
from rest_framework import status

import djoser.views
from djoser.compat import get_user_email
from djoser.conf import settings as default_settings
from .common import create_user, mock
from testapp.models import CustomUser


class PasswordResetViewTest(restframework.APIViewTestCase,
                            assertions.StatusCodeAssertionsMixin,
                            assertions.EmailAssertionsMixin):
    view_class = djoser.views.PasswordResetView

    def test_post_should_send_email_to_user_with_password_reset_link(self):
        user = create_user()
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
        site = get_current_site(request)
        self.assertIn(site.domain, mail.outbox[0].body)
        self.assertIn(site.name, mail.outbox[0].body)
    
    def test_post_should_send_email_to_user_with_origin_domain(self):
        domain = 'example.com'
        user = create_user()
        data = {'email': user.email}
        request = self.factory.post(data=data, HTTP_ORIGIN=domain)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
        self.assertIn(domain, mail.outbox[0].body)

    def test_post_send_email_to_user_with_request_domain_and_site_name(self):
        user = create_user()
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        self.view(request)

        self.assertIn(request.get_host(), mail.outbox[0].body)

    def test_post_should_not_send_email_to_user_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(0)

    def test_post_should_return_no_content_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(
        DJOSER=dict(settings.DJOSER,
                    **{'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True}))
    def test_post_should_return_bad_request_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['email'][0], default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND
        )

    @mock.patch(
        'djoser.serializers.User', CustomUser)
    @mock.patch(
        'djoser.views.User', CustomUser)
    @override_settings(
        AUTH_USER_MODEL='testapp.CustomUser')
    def test_post_should_send_email_to_custom_user_with_password_reset_link(self):
        user = create_user(use_custom_data=True)
        data = {
            'custom_email': get_user_email(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[get_user_email(user)])
        site = get_current_site(request)
        self.assertIn(site.domain, mail.outbox[0].body)
        self.assertIn(site.name, mail.outbox[0].body)

    @mock.patch(
        'djoser.serializers.User', CustomUser)
    @mock.patch(
        'djoser.views.User', CustomUser)
    @override_settings(
        AUTH_USER_MODEL='testapp.CustomUser',
        DJOSER=dict(settings.DJOSER,
                    **{'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True}))
    def test_post_should_return_bad_request_with_custom_email_field_if_user_does_not_exist(self):
        data = {
            'custom_email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['custom_email'][0], default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND
        )
