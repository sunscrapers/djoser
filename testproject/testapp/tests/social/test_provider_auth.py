from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import six
from djet import assertions, restframework
from rest_framework import status
from social_core.exceptions import AuthException

import djoser.social.views

from ..common import create_user, mock


class ProviderAuthViewTestCase(
    restframework.APIViewTestCase, assertions.StatusCodeAssertionsMixin
):
    view_class = djoser.social.views.ProviderAuthView
    middleware = [SessionMiddleware]

    def test_get_facebook_provider_fails_if_no_redirect_uri(self):
        request = self.factory.get()
        response = self.view(request, provider="facebook")

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_get_facebook_provider_fails_if_wrong_redirect_uri(self):
        request = self.factory.get(data={"redirect_uri": "http://yolo.com/"})
        response = self.view(request, provider="facebook")

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_get_facebook_provider_provides_valid_authorization_url(self):
        request = self.factory.get(data={"redirect_uri": "http://test.localhost/"})
        response = self.view(request, provider="facebook")

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertIn("authorization_url", response.data)

    def test_post_facebook_provider_success_returns_token(self):
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            return_value=create_user(),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post()
        request.GET = {k: v for k, v in six.iteritems(data)}
        response = self.view(request, provider="facebook")
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {"access", "refresh", "user"})

    def test_post_facebook_provider_code_validation_fails(self):
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthException(backend=None),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post()
        request.GET = {k: v for k, v in six.iteritems(data)}
        response = self.view(request, provider="facebook")
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_facebook_provider_validation_fails_if_invalid_state(self):
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"][::-1],
        ).start()

        request = self.factory.post()
        request.GET = {k: v for k, v in six.iteritems(data)}
        response = self.view(request, provider="facebook")
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
