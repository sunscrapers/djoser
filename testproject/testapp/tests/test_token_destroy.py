from django.contrib.auth import user_logged_out
from djet import assertions, restframework
from rest_framework import status
import djoser.constants
import djoser.utils
import djoser.views

from .common import create_user


class TokenDestroyViewTest(restframework.APIViewTestCase,
                           assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.TokenDestroyView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_logout_logged_in_user(self):
        user = create_user()
        user_logged_out.connect(self.signal_receiver)
        request = self.factory.post(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
        self.assertTrue(self.signal_sent)

    def test_post_should_deny_logging_out_when_user_not_logged_in(self):
        create_user()
        request = self.factory.post()

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_options(self):
        user = create_user()
        request = self.factory.options(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
