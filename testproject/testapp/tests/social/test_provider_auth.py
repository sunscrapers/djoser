import pytest
from testapp.factories import UserFactory
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_core.exceptions import (
    AuthException,
    AuthCanceled,
    AuthUnknownError,
    SocialAuthBaseException,
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
        assert response.data == {
            "non_field_errors": ["Invalid state has been provided."]
        }

    def test_post_facebook_provider_validation_fails_if_session_state_missing(
        self,
    ):
        data = {"code": "XYZ", "state": "ABC"}

        with mock.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=None,
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "non_field_errors": [
                "State could not be found in server-side session data."
            ]
        }

    def test_post_facebook_provider_validation_fails_if_request_state_empty(self):
        data = {"code": "XYZ", "state": "ABC"}

        with (
            mock.patch(
                "social_core.backends.oauth.OAuthAuth.get_session_state",
                return_value=data["state"],
            ),
            mock.patch(
                "social_core.backends.oauth.OAuthAuth.get_request_state",
                return_value="",
            ),
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "non_field_errors": ["State could not be found in request data."]
        }

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

    def test_post_facebook_provider_validation_reports_unknown_state_error(self):
        """
        A state error djoser has no dedicated message for is still a 400 and
        surfaces the exception's own text.
        """
        data = {"code": "XYZ", "state": "ABC"}
        error = AuthException(None, "something else went wrong")

        with mock.patch(
            "social_core.backends.oauth.OAuthAuth.validate_state",
            side_effect=error,
        ):
            request = self.factory.post("/auth/facebook/")
            request.GET = {k: v for k, v in data.items()}
            response = self._get_view_response(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"non_field_errors": [str(error)]}

    def test_get_unsupported_provider_returns_404(self):
        """
        Test that unsupported providers return 404.
        """
        request = self.factory.get(
            "/auth/unsupported/", data={"redirect_uri": "http://test.localhost/"}
        )
        response = self._get_view_response(request, provider="unsupported")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_provider_reraises_other_backend_errors(self):
        """
        Only a missing backend maps to 404; other social-auth errors propagate.
        """
        request = self.factory.get(
            "/auth/facebook/", data={"redirect_uri": "http://test.localhost/"}
        )
        with (
            mock.patch(
                "djoser.social.views.load_backend",
                side_effect=SocialAuthBaseException(None, "misconfigured"),
            ),
            pytest.raises(SocialAuthBaseException),
        ):
            self._get_view_response(request, provider="facebook")
