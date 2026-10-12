"""
Method handling and URL behaviour of the 3.0 view split, measured against 2.x.

The first group pins behaviour 2.x had and 3.0 keeps: HEAD, OPTIONS and unmapped methods
go through DRF, so authentication runs first and the client gets DRF's own 401, JSON 405
or OPTIONS metadata. The second group pins the four places where 3.0 deliberately
differs from 2.x; each is listed as a breaking change in the changelog.
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


# --- kept from 2.x ------------------------------------------------------------


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


# --- 3.0 departures from 2.x -------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "hide_users, expected_status", [(True, 404), (False, 403)], ids=["hidden", "shown"]
)
def test_me_delete_denied_follows_hide_users(parity_user, hide_users, expected_status):
    """
    2.x excluded the `me` action from HIDE_USERS, so a denied /users/me/ was a 403.

    3.0 treats `me` like every other user endpoint: HIDE_USERS turns the denial into
    a 404 so the endpoint reveals nothing about the account.
    """
    client = APIClient()
    client.force_authenticate(user=parity_user)
    with override_settings(
        DJOSER={
            "HIDE_USERS": hide_users,
            "PERMISSIONS": {"user_delete": ["rest_framework.permissions.IsAdminUser"]},
        }
    ):
        response = client.delete("/auth/users/me/")
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_no_api_root(auth_client):
    """
    2.x mounted a DRF DefaultRouter, whose api-root made GET /auth/ a live endpoint.

    3.0 URL configs are hand-written, so the prefix itself is not a resource.
    """
    assert auth_client.get("/auth/").status_code == 404


@pytest.mark.django_db
def test_slashless_token_login_redirects_with_308(parity_user):
    """
    2.x matched token URLs with an optional trailing slash and served them directly.

    3.0 redirects to the canonical slash-terminated URL with a 308, which keeps the
    POST method and body (see test_urls for the full set of redirected paths).
    """
    response = APIClient().post(
        "/auth/token/login",
        {"username": "parity", "password": "secret123!"},
        format="json",
    )
    assert response.status_code == 308
    assert response["Location"] == "/auth/token/login/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/auth/jwt/create/", 200),
        ("/auth/jwt/create", 308),
        ("/auth/jwt/create/extra", 404),
        ("/auth/jwt/createx", 404),
    ],
)
def test_jwt_create_urls_are_anchored(parity_user, path, expected_status):
    """
    2.x jwt regexes were unanchored, so /auth/jwt/createx and /auth/jwt/create/extra
    resolved to the same view as /auth/jwt/create/.

    3.0 matches the exact path; only the slash-less form is redirected.
    """
    response = APIClient().post(
        path, {"username": "parity", "password": "secret123!"}, format="json"
    )
    assert response.status_code == expected_status
