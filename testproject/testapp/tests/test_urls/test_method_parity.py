"""
Pins djoser 2.x method-handling behavior so the 3.0 view split can prove parity.

Every test in this module must pass on master unchanged. If an assertion below
disagrees with master's actual behavior, fix the TEST to pin what master does —
never the other way around.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def parity_user(db):
    return User.objects.create_user(
        username="parity", email="parity@example.com", password="secret123!"
    )


@pytest.fixture
def auth_client(parity_user):
    client = APIClient()
    client.force_authenticate(user=parity_user)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    ["/auth/users/", "/auth/users/activation/", "/auth/users/reset_password/"],
)
def test_options_returns_200_for_authenticated_clients(auth_client, path):
    assert auth_client.options(path).status_code == 200


@pytest.mark.django_db
def test_options_on_user_detail_returns_200(auth_client, parity_user):
    assert auth_client.options(f"/auth/users/{parity_user.pk}/").status_code == 200


@pytest.mark.django_db
def test_head_is_supported_wherever_get_is(auth_client, parity_user):
    assert auth_client.head("/auth/users/").status_code == 200
    assert auth_client.head(f"/auth/users/{parity_user.pk}/").status_code == 200


@pytest.mark.django_db
def test_options_runs_authentication_first(db):
    # DRF runs authentication/permissions before the options handler,
    # so anonymous clients get 401, not metadata.
    assert APIClient().options("/auth/users/").status_code == 401


@pytest.mark.django_db
def test_unmapped_method_gets_drf_json_405_after_auth(auth_client):
    response = auth_client.put("/auth/users/", {}, format="json")
    assert response.status_code == 405
    assert response["Content-Type"].startswith("application/json")
    assert "detail" in response.data


@pytest.mark.django_db
def test_unmapped_method_gets_401_for_anonymous_clients(db):
    assert APIClient().put("/auth/users/", {}, format="json").status_code == 401


@pytest.mark.django_db
def test_me_delete_returns_403_not_404_when_permission_denied(parity_user):
    """
    HIDE_USERS (default True) converts 403->404 for user list/detail, but the
    2.x `me` action was deliberately excluded — a denied /users/me/ request
    answers a plain 403. DELETE is used because its permission (user_delete)
    is resolved at request time, so the override below actually applies.
    """
    client = APIClient()
    client.force_authenticate(user=parity_user)
    with override_settings(
        DJOSER={
            "PERMISSIONS": {"user_delete": ["rest_framework.permissions.IsAdminUser"]}
        }
    ):
        response = client.delete("/auth/users/me/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_root_lists_users_endpoint(auth_client):
    """DefaultRouter's api-root at the include prefix: GET /auth/ is a live endpoint."""
    response = auth_client.get("/auth/")
    assert response.status_code == 200
    assert "users" in response.data


@pytest.mark.django_db
def test_slashless_token_login_serves_request_directly(parity_user):
    """2.x matched token URLs with an optional trailing slash — no redirect."""
    response = APIClient().post(
        "/auth/token/login",
        {"username": "parity", "password": "secret123!"},
        format="json",
    )
    assert response.status_code == 200
    assert "auth_token" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/auth/jwt/create",
        "/auth/jwt/create/",
        "/auth/jwt/create/extra",
        "/auth/jwt/createx",
    ],
)
def test_jwt_create_matches_with_and_without_anchor(parity_user, path):
    """2.x jwt regexes were unanchored — all of these resolve to the same view."""
    response = APIClient().post(
        path, {"username": "parity", "password": "secret123!"}, format="json"
    )
    assert response.status_code == 200
