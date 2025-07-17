import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from rest_framework import status
from social_core.exceptions import AuthException

import djoser.social.views


User = get_user_model()


@pytest.fixture
def view():
    return djoser.social.views.ProviderAuthView.as_view()


# Apply middleware if needed for session state
@pytest.mark.django_db
class TestProviderAuthView:
    # Removed APIViewTestCase and mixins

    def test_get_facebook_provider_fails_if_no_redirect_uri(self, rf, view):
        request = rf.get("/", data={})
        # Add session middleware manually since RequestFactory doesn't include middleware # noqa: E501
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_facebook_provider_fails_if_wrong_redirect_uri(self, rf, view):
        request = rf.get("/", data={"redirect_uri": "http://yolo.com/"})
        # Add session middleware manually since RequestFactory doesn't include middleware  # noqa: E501
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_facebook_provider_provides_valid_authorization_url(self, rf, view):
        request = rf.get("/", data={"redirect_uri": "http://test.localhost/"})
        # Add session middleware manually since RequestFactory doesn't include middleware  # noqa: E501
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_200_OK
        assert "authorization_url" in response.data

    def test_post_facebook_provider_success_returns_token(self, rf, view, user, mocker):
        data = {"code": "XYZ", "state": "ABC"}

        mocker.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            return_value=user,
        )
        mocker.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        )

        request = rf.post(
            f"/?code={data['code']}&state={data['state']}"
        )  # Add query params
        # Add session middleware if state is stored in session
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_201_CREATED
        # Adjust expected keys based on actual token implementation (JWT/AuthToken)
        assert "access" in response.data or "auth_token" in response.data

    def test_post_facebook_provider_code_validation_fails(self, rf, view, mocker):
        data = {"code": "XYZ", "state": "ABC"}

        mocker.patch(
            "social_core.backends.facebook.FacebookOAuth2.auth_complete",
            side_effect=AuthException(backend=None),
        )
        mocker.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"],
        )

        request = rf.post(f"/?code={data['code']}&state={data['state']}")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_facebook_provider_validation_fails_if_invalid_state(
        self, rf, view, mocker
    ):
        data = {"code": "XYZ", "state": "ABC"}

        mocker.patch(
            "social_core.backends.oauth.OAuthAuth.get_session_state",
            return_value=data["state"][::-1],  # Invalid state
        )

        request = rf.post(f"/?code={data['code']}&state={data['state']}")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        response = view(request, provider="facebook")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
