import pytest
from testapp.factories import UserFactory
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_core.exceptions import (
    AuthException,
    AuthForbidden,
    AuthCanceled,
    AuthUnknownError,
)

import djoser.social.views

from unittest import mock


@pytest.mark.django_db
class TestProviderAuthView:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = APIRequestFactory()
        self.view_class = djoser.social.views.ProviderAuthView

    def _get_view_response(self, request, **kwargs):
        """Helper to get view response with middleware applied"""
        view = self.view_class.as_view()
        # Apply middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return view(request, **kwargs)

    def test_get_facebook_provider_fails_if_no_redirect_uri(self):
        request = self.factory.get("/auth/facebook/")
        response = self._get_view_response(request, provider="facebook")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_facebook_provider_fails_if_wrong_redirect_uri(self):
        request = self.factory.get(
            "/auth/facebook/", data={"redirect_uri": "http://yolo.com/"}
        )
        response = self._get_view_response(request, provider="facebook")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_facebook_provider_provides_valid_authorization_url(self):
        request = self.factory.get(
            "/auth/facebook/", data={"redirect_uri": "http://test.localhost/"}
        )
        response = self._get_view_response(request, provider="facebook")

        assert response.status_code == status.HTTP_200_OK
        assert "authorization_url" in response.data

    def test_post_facebook_provider_success_returns_token(self):
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            return_value=UserFactory.create(),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.data.keys()) == {"access", "refresh", "user"}

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

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_validation_fails_if_invalid_state(self):
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"][::-1],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_auth_forbidden_error(self):
        """Test handling of AuthForbidden exception."""
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthForbidden(backend=None),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_auth_canceled_error(self):
        """Test handling of AuthCanceled exception."""
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthCanceled(backend=None),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_auth_unknown_error(self):
        """Test handling of AuthUnknownError exception."""
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthUnknownError(backend=None),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = {k: v for k, v in data.items()}
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_missing_code_parameter(self):
        """Test handling of missing code parameter."""
        data = {"state": "ABC"}  # Missing code

        request = self.factory.post("/auth/facebook/")
        request.GET = data
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_missing_state_parameter(self):
        """Test handling of missing state parameter."""
        data = {"code": "XYZ"}  # Missing state

        request = self.factory.post("/auth/facebook/")
        request.GET = data
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_unsupported_provider_returns_404(self):
        """Test that unsupported providers return 404."""
        request = self.factory.get(
            "/auth/unsupported/", data={"redirect_uri": "http://test.localhost/"}
        )
        response = self._get_view_response(request, provider="unsupported")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_post_with_expired_authorization_code(self):
        """Test handling of expired authorization code."""
        data = {"code": "EXPIRED_CODE", "state": "ABC"}

        # Create a mock backend
        mock_backend = mock.Mock()

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthException(mock_backend),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = data
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_network_error_during_auth(self):
        """Test handling of network errors during authentication."""
        data = {"code": "XYZ", "state": "ABC"}

        mock.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=ConnectionError("Network error"),
        ).start()
        mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        ).start()

        request = self.factory.post("/auth/facebook/")
        request.GET = data
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
