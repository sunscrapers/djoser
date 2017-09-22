from django.core import mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.test.utils import override_settings

from djet import assertions, restframework
from rest_framework import status

import djoser.constants
import djoser.views

from .common import create_user


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
            response.data['email'][0], djoser.constants.EMAIL_NOT_FOUND
        )
