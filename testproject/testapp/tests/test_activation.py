from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.test.utils import override_settings
from djet import assertions, restframework, utils
from rest_framework import status
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
        user = utils.refresh(user)
        self.assertTrue(user.is_active)

    def test_post_respond_with_bad_request_when_wrong_uid(self):
        data = {
            'uid': djoser.utils.encode_uid(1),
        }
        request = self.factory.post(data=data)

        response = self.view(request)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

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
        self.assertFalse(self.signal_sent)

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
