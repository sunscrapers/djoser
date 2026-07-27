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
    AuthMissingParameter,
    AuthStateMissing,
)

import djoser.social.views

from unittest import mock


def test_social_auth_missing_state_request():
    from djoser.social.serializers import ProviderAuthSerializer

    serializer = ProviderAuthSerializer()

    with mock.patch("djoser.social.serializers.load_strategy") as mock_load_strategy:
        mock_strategy = mock.Mock()
        mock_load_strategy.return_value = mock_strategy
        mock_strategy.backend.auth_complete.side_effect = AuthMissingParameter(
            mock.Mock(), "state"
        )

        with pytest.raises(Exception):  # Should raise ValidationError
            serializer.validate({"provider": "facebook", "access_token": "token"})


def test_social_auth_missing_state_session():
    from djoser.social.serializers import ProviderAuthSerializer

    serializer = ProviderAuthSerializer()

    with mock.patch("djoser.social.serializers.load_strategy") as mock_load_strategy:
        mock_strategy = mock.Mock()
        mock_load_strategy.return_value = mock_strategy
        mock_strategy.backend.auth_complete.side_effect = AuthStateMissing(
            mock.Mock(), "state"
        )

        with pytest.raises(Exception):  # Should raise ValidationError
            serializer.validate({"provider": "facebook", "access_token": "token"})


@pytest.mark.django_db
class TestProviderAuthView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = APIRequestFactory()
        self.view_class = djoser.social.views.ProviderAuthView

    def _get_view_response(self, request, **kwargs):
        """
        Helper to get view response with middleware applied.
        """
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

        with (
            mock.patch(
                "social_core.backends.facebook.FacebookOAuth2.auth_complete",
                return_value=UserFactory.create(),
            ),
            mock.patch(
                "social_core.backends.oauth.OAuthAuth.get_session_state",
                return_value=data["state"],
            ),
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.data.keys()) == {"access", "refresh", "user"}

    @pytest.mark.parametrize(
        "auth_error",
        [
            AuthException(backend=None),
            AuthForbidden(backend=None),
            AuthCanceled(backend=None),
            AuthUnknownError(backend=None),
            ConnectionError("Network error"),
        ],
        ids=lambda e: type(e).__name__,
    )
    def test_post_facebook_provider_fails_if_auth_complete_raises(self, auth_error):
        data = {"code": "XYZ", "state": "ABC"}

        with (
            mock.patch(
                "social_core.backends.facebook.FacebookOAuth2.auth_complete",
                side_effect=auth_error,
            ),
            mock.patch(
                "social_core.backends.oauth.OAuthAuth.get_session_state",
                return_value=data["state"],
            ),
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_validation_fails_if_invalid_state(self):
        data = {"code": "XYZ", "state": "ABC"}

        with mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"][::-1],
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "data",
        [{"state": "ABC"}, {"code": "XYZ"}],
        ids=["missing-code", "missing-state"],
    )
    def test_post_facebook_provider_missing_required_parameter(self, data):
        request = self.factory.post("/auth/facebook/")
        request.GET = data
        response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_unsupported_provider_returns_404(self):
        """
        Test that unsupported providers return 404.
        """
        request = self.factory.get(
            "/auth/unsupported/", data={"redirect_uri": "http://test.localhost/"}
        )
        response = self._get_view_response(request, provider="unsupported")

        assert response.status_code == status.HTTP_404_NOT_FOUND
