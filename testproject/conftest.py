import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

User = get_user_model()


def create_user(
    model: type[User] = User,
    **kwargs,
):
    """Context manager for creating and cleaning up temporary users."""
    defaults = {
        "username": "temp_user",
        "email": "temp@example.com",
        "password": "temp_password",
    }
    defaults.update(kwargs)

    user = model.objects.create_user(**defaults)
    user.raw_password = defaults["password"]

    return user


@pytest.fixture
def user(db):
    """Create a standard test user."""
    yield create_user(username="john", email="john@beatles.com", password="secret")


@pytest.fixture
def other_user(db):
    """Create another test user for multi-user scenarios."""
    yield create_user(username="paul", email="paul@beatles.com", password="verysecret")


@pytest.fixture
def superuser(db):
    yield create_user(
        username="admin",
        email="admin@beatles.com",
        password="admin123",
        is_superuser=True,
        is_active=True,
    )


@pytest.fixture
def custom_user(db):
    from testapp.models import CustomUser

    yield create_user(
        model=CustomUser,
        custom_username="john",
        custom_email="john@beatles.com",
        custom_required_field="42",
        password="secret",
    )


@pytest.fixture
def inactive_user(db):
    yield create_user(
        username="inactive",
        email="inactive@beatles.com",
        password="secret",
        is_active=False,
    )


@pytest.fixture
def anonymous_api_client():
    """Create an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def api_client(user):
    """Create an authenticated API client with token and session auth."""
    from djoser.conf import settings as djoser_settings

    client = APIClient()

    # Create token for token-based authentication tests
    if djoser_settings.TOKEN_MODEL:
        token, _ = djoser_settings.TOKEN_MODEL.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    # Force authenticate for session-based tests
    client.force_authenticate(user=user)

    # Create session for session-based tests
    client.force_login(user)

    return client


@pytest.fixture
def custom_url():
    """Generate URL for custom user reset endpoint."""
    from testapp.models import CustomUser

    return reverse(f"user-reset-{CustomUser.USERNAME_FIELD}")
