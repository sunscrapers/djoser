from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.test.utils import override_settings
from djet import assertions, restframework
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

import djoser.constants
import djoser.signals
import djoser.utils
import djoser.views

from .common import create_user


class ActivationViewTest(restframework.APIViewTestCase,
                         assertions.EmailAssertionsMixin,
                         assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.ActivationView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_activate_user_and_not_login(self):
        user = create_user()
        user.is_active = False
        user.save()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_post_respond_with_bad_request_when_wrong_uid(self):
        user = create_user()
        data = {
            'uid': 'wrong-uid',
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.data.keys()), ['uid'])
        self.assertEqual(
            response.data['uid'],
            [djoser.constants.INVALID_UID_ERROR]
        )

    def test_post_respond_with_bad_request_when_stale_token(self):
        user = create_user()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(list(response.data.keys()), ['detail'])
        self.assertEqual(
            response.data['detail'],
            djoser.constants.STALE_TOKEN_ERROR
        )
        self.assertFalse(self.signal_sent)

    def test_post_respond_with_bad_request_when_wrong_token(self):
        user = create_user()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': 'wrong-token',
        }
        request = self.factory.post(data=data)

        response = self.view(request)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.data.keys()), ['token'])
        self.assertEqual(
            response.data['token'],
            [djoser.constants.INVALID_TOKEN_ERROR]
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_CONFIRMATION_EMAIL': True})
    )
    def test_post_sent_confirmation_email(self):
        user = create_user()
        user.is_active = False
        user.save()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])


class UserViewSetConfirmationTest(APITestCase,
                                  assertions.EmailAssertionsMixin,
                                  assertions.StatusCodeAssertionsMixin):

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_activate_user_and_not_login(self):
        user = create_user()
        user.is_active = False
        user.save()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        response = self.client.post(reverse('user-confirm'), data=data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_post_respond_with_bad_request_when_wrong_uid(self):
        user = create_user()
        data = {
            'uid': 'wrong-uid',
            'token': default_token_generator.make_token(user),
        }
        response = self.client.post(reverse('user-confirm'), data=data)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.data.keys()), ['uid'])
        self.assertEqual(
            response.data['uid'],
            [djoser.constants.INVALID_UID_ERROR]
        )

    def test_post_respond_with_bad_request_when_stale_token(self):
        user = create_user()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        response = self.client.post(reverse('user-confirm'), data=data)

        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(list(response.data.keys()), ['detail'])
        self.assertEqual(
            response.data['detail'],
            djoser.constants.STALE_TOKEN_ERROR
        )
        self.assertFalse(self.signal_sent)

    def test_post_respond_with_bad_request_when_wrong_token(self):
        user = create_user()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': 'wrong-token',
        }
        response = self.client.post(reverse('user-confirm'), data=data)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.data.keys()), ['token'])
        self.assertEqual(
            response.data['token'],
            [djoser.constants.INVALID_TOKEN_ERROR]
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SEND_CONFIRMATION_EMAIL': True})
    )
    def test_post_sent_confirmation_email(self):
        user = create_user()
        user.is_active = False
        user.save()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        response = self.client.post(reverse('user-confirm'), data=data)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
