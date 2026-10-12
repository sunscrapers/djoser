"""
Pins how djoser 2.x applies DJOSER["PERMISSIONS"] and HIDE_USERS to its endpoints.

Every test in this module must pass on master unchanged. If an assertion below
disagrees with master's actual behavior, fix the TEST to pin what master does —
never the other way around.

Projects customise permissions in two ways, and both are covered:

* in settings.py, before djoser is imported. The ``djoser_startup_settings`` fixture
  emulates this by importing djoser's views and URLs again under the given settings.
* in their own test suites, with ``override_settings(DJOSER=...)`` once djoser's URLs
  and views have been imported (the ``urls_imported`` fixture makes sure they were).

The custom permissions are plain DRF permission classes named by dotted path, as in a
settings.py. Each one records the PERMISSIONS key it was configured for and what it
saw of the view, and allows the request unless that key is in DENIED_KEYS.
"""

from unittest import mock

import pytest
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import resolve
from rest_framework.permissions import BasePermission
from rest_framework.test import APIClient
from rest_framework.views import APIView

User = get_user_model()

MISSING = "<missing>"
PERMISSION_KEYS = (
    "activation",
    "password_reset",
    "password_reset_confirm",
    "set_password",
    "username_reset",
    "username_reset_confirm",
    "set_username",
    "user_create",
    "user_delete",
    "user",
    "user_list",
    "token_create",
    "token_destroy",
)
CALLS = []
DENIED_KEYS = set()


class RecordingPermission(BasePermission):
    key = None

    def has_permission(self, request, view):
        return self.record("has_permission", view)

    def has_object_permission(self, request, view, obj):
        return self.record("has_object_permission", view)

    def record(self, kind, view):
        CALLS.append(
            {
                "key": self.key,
                "kind": kind,
                "action": getattr(view, "action", MISSING),
                "kwargs": dict(view.kwargs),
            }
        )
        return self.key not in DENIED_KEYS


# One recording class per key, set on this module so settings can name it by path.
RECORDING_PERMISSIONS = {}
for _key in PERMISSION_KEYS:
    _name = f"Record_{_key}"
    globals()[_name] = type(_name, (RecordingPermission,), {"key": _key})
    RECORDING_PERMISSIONS[_key] = [f"{__name__}.{_name}"]


def request_ids(requests):
    return [f"{request[0]} {request[1]}" for request in requests]


# Every route and method 2.x served with an action: (method, path, key, view.action).
# {pk} is the requesting user's own primary key. HEAD /auth/users/me/ is left out
# because it is a 500 on 2.x. The token views never had an action.
ENDPOINTS = [
    ("GET", "/auth/users/", "user_list", "list"),
    ("HEAD", "/auth/users/", "user_list", "list"),
    ("POST", "/auth/users/", "user_create", "create"),
    ("GET", "/auth/users/{pk}/", "user", "retrieve"),
    ("HEAD", "/auth/users/{pk}/", "user", "retrieve"),
    ("PUT", "/auth/users/{pk}/", "user", "update"),
    ("PATCH", "/auth/users/{pk}/", "user", "partial_update"),
    ("DELETE", "/auth/users/{pk}/", "user_delete", "destroy"),
    ("GET", "/auth/users/me/", "user", "me"),
    ("PUT", "/auth/users/me/", "user", "me"),
    ("PATCH", "/auth/users/me/", "user", "me"),
    ("DELETE", "/auth/users/me/", "user_delete", "me"),
    ("POST", "/auth/users/activation/", "activation", "activation"),
    ("POST", "/auth/users/resend_activation/", "password_reset", "resend_activation"),
    ("POST", "/auth/users/reset_password/", "password_reset", "reset_password"),
    (
        "POST",
        "/auth/users/reset_password_confirm/",
        "password_reset_confirm",
        "reset_password_confirm",
    ),
    ("POST", "/auth/users/set_password/", "set_password", "set_password"),
    ("POST", "/auth/users/set_username/", "set_username", "set_username"),
    ("POST", "/auth/users/reset_username/", "username_reset", "reset_username"),
    (
        "POST",
        "/auth/users/reset_username_confirm/",
        "username_reset_confirm",
        "reset_username_confirm",
    ),
    ("POST", "/auth/token/login/", "token_create", None),
    ("POST", "/auth/token/logout/", "token_destroy", None),
]
ACTION_ENDPOINTS = [endpoint for endpoint in ENDPOINTS if endpoint[3] is not None]

# The endpoints whose key 2.x looked up on every request. "user", "token_create" and
# "token_destroy" were class attributes, read once when djoser.views was imported.
REQUEST_TIME_ENDPOINTS = [
    (method, path, key)
    for method, path, key, _action in ENDPOINTS
    if key not in ("user", "token_create", "token_destroy")
]

ACTION_PATHS = [
    "/auth/users/activation/",
    "/auth/users/resend_activation/",
    "/auth/users/reset_password/",
    "/auth/users/reset_password_confirm/",
    "/auth/users/set_password/",
    "/auth/users/set_username/",
    "/auth/users/reset_username/",
    "/auth/users/reset_username_confirm/",
]
# OPTIONS, and methods a route does not serve. 2.x's UserViewSet handled them with
# the "metadata" action or none. OPTIONS /auth/users/me/ is a 500 on 2.x.
NO_ACTION_REQUESTS = [
    ("OPTIONS", "/auth/users/"),
    ("PUT", "/auth/users/"),
    ("DELETE", "/auth/users/"),
    ("OPTIONS", "/auth/users/{pk}/"),
    ("POST", "/auth/users/{pk}/"),
    ("POST", "/auth/users/me/"),
    *[(method, path) for path in ACTION_PATHS for method in ("GET", "OPTIONS")],
]


@pytest.fixture(autouse=True)
def _reset_recorders():
    CALLS.clear()
    DENIED_KEYS.clear()
    yield
    CALLS.clear()
    DENIED_KEYS.clear()


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="regular", email="regular@example.com")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", email="other@example.com")


@pytest.fixture
def djoser_configured(djoser_startup_settings):
    """
    Return a context manager running code as if settings.py had set DJOSER to the
    project's DJOSER updated with the given keys.
    """

    def configure(**djoser):
        return djoser_startup_settings({**django_settings.DJOSER, **djoser})

    return configure


@pytest.fixture
def urls_imported():
    """
    Import djoser's URLs and views under the project's settings.

    A running test suite has done this before it reaches override_settings. Without it,
    whatever djoser reads at import time would come from the override.
    """
    for _method, path, _key, _action in ENDPOINTS:
        resolve(path.format(pk=1))


def send(method, path, user=None, data="{}"):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client.generic(method, path, data, content_type="application/json")


# --- which PERMISSIONS key governs which endpoint ------------------------------


@pytest.mark.parametrize(
    "method, path, key, action", ENDPOINTS, ids=request_ids(ENDPOINTS)
)
def test_permissions_key_set_at_startup_governs_endpoint(
    djoser_configured, regular_user, method, path, key, action
):
    """
    Includes the 2.x quirks: resend_activation/ is governed by password_reset, and
    DELETE /auth/users/me/ by user_delete while its other methods use user.
    """
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        send(method, path.format(pk=regular_user.pk), regular_user)
    assert {call["key"] for call in CALLS} == {key}


@pytest.mark.parametrize(
    "method, path, key",
    REQUEST_TIME_ENDPOINTS,
    ids=request_ids(REQUEST_TIME_ENDPOINTS),
)
def test_permissions_key_changed_by_override_settings_governs_endpoint(
    urls_imported, regular_user, method, path, key
):
    djoser = {**django_settings.DJOSER, "PERMISSIONS": RECORDING_PERMISSIONS}
    with override_settings(DJOSER=djoser):
        send(method, path.format(pk=regular_user.pk), regular_user)
    assert {call["key"] for call in CALLS} == {key}


@pytest.mark.parametrize(
    "method, path, key",
    REQUEST_TIME_ENDPOINTS,
    ids=request_ids(REQUEST_TIME_ENDPOINTS),
)
def test_permissions_in_force_when_views_were_imported_do_not_outlive_it(
    djoser_configured, regular_user, method, path, key
):
    """
    Later requests follow the real settings, not the ones in force at import time.

    A test run whose first request happens inside override_settings imports djoser's
    views under that override.
    """
    project_djoser = dict(django_settings.DJOSER)
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        # The override has ended, but the views imported under it are still in use.
        with override_settings(DJOSER=project_djoser):
            send(method, path.format(pk=regular_user.pk), regular_user)
    assert CALLS == []


@pytest.mark.parametrize(
    "method, path", NO_ACTION_REQUESTS, ids=request_ids(NO_ACTION_REQUESTS)
)
def test_options_and_unmapped_methods_are_governed_by_user_key(
    djoser_configured, regular_user, method, path
):
    """
    2.x checked OPTIONS and methods a /users/ route does not serve against
    UserViewSet.permission_classes, i.e. PERMISSIONS["user"], whatever the route.
    """
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        send(method, path.format(pk=regular_user.pk), regular_user)
    assert {call["key"] for call in CALLS} == {"user"}


def test_drf_default_permission_classes_are_never_consulted(regular_user):
    """
    Every djoser endpoint uses a DJOSER["PERMISSIONS"] key, so a project's strict
    REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] cannot lock users out of djoser.
    """
    default = type("RecordDefault", (RecordingPermission,), {"key": "DEFAULT"})
    requests = [endpoint[:2] for endpoint in ENDPOINTS] + NO_ACTION_REQUESTS
    with mock.patch.object(APIView, "permission_classes", [default]):
        for method, path in requests:
            send(method, path.format(pk=regular_user.pk), regular_user)
    assert "DEFAULT" not in {call["key"] for call in CALLS}


# --- what a custom permission sees and how often it is asked ------------------


@pytest.mark.parametrize(
    "method, path, key, action", ACTION_ENDPOINTS, ids=request_ids(ACTION_ENDPOINTS)
)
def test_custom_permission_sees_view_action(
    djoser_configured, regular_user, method, path, key, action
):
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        send(method, path.format(pk=regular_user.pk), regular_user)
    assert {call["action"] for call in CALLS} == {action}


@pytest.mark.parametrize(
    "method, path, key, action", ENDPOINTS, ids=request_ids(ENDPOINTS)
)
def test_custom_permission_sees_view_kwargs(
    djoser_configured, regular_user, method, path, key, action
):
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        send(method, path.format(pk=regular_user.pk), regular_user)
    expected = {User._meta.pk.name: str(regular_user.pk)} if "{pk}" in path else {}
    seen = [call["kwargs"] for call in CALLS]
    assert seen
    assert seen == [expected] * len(seen)


@pytest.mark.parametrize(
    "method, path, key, action", ENDPOINTS, ids=request_ids(ENDPOINTS)
)
def test_custom_permission_call_counts(
    djoser_configured, regular_user, method, path, key, action
):
    """
    has_permission runs once per request, has_object_permission only on {pk} URLs.

    The object check runs once on /auth/users/{pk}/ and never on /auth/users/me/ or the
    other endpoints.
    """
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS):
        send(method, path.format(pk=regular_user.pk), regular_user)
    kinds = [call["kind"] for call in CALLS]
    assert kinds.count("has_permission") == 1
    assert kinds.count("has_object_permission") == (1 if "{pk}" in path else 0)


# --- HIDE_USERS ---------------------------------------------------------------

# Denied requests on the list and detail routes, with their status under HIDE_USERS.
# Without HIDE_USERS each one is a 403. DELETE was never hidden.
DENIED_USER_REQUESTS = [
    ("GET", "/auth/users/", 404),
    ("HEAD", "/auth/users/", 404),
    *[
        (method, path, 404)
        for path in ("/auth/users/{pk}/", "/auth/users/{other}/")
        for method in ("GET", "HEAD", "PUT", "PATCH")
    ],
    ("DELETE", "/auth/users/{pk}/", 403),
    ("DELETE", "/auth/users/{other}/", 403),
]


@pytest.mark.parametrize("hide_users", [True, False], ids=["hidden", "shown"])
@pytest.mark.parametrize("authenticated", [True, False], ids=["user", "anonymous"])
def test_hide_users_status_of_denied_list_and_detail_requests(
    djoser_configured, regular_user, other_user, authenticated, hide_users
):
    DENIED_KEYS.update(PERMISSION_KEYS)
    user = regular_user if authenticated else None
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS, HIDE_USERS=hide_users):
        statuses = {
            f"{method} {path}": send(
                method, path.format(pk=regular_user.pk, other=other_user.pk), user
            ).status_code
            for method, path, _hidden_status in DENIED_USER_REQUESTS
        }
    expected = {}
    for method, path, hidden_status in DENIED_USER_REQUESTS:
        if not authenticated:
            expected[f"{method} {path}"] = 401
        else:
            expected[f"{method} {path}"] = hidden_status if hide_users else 403
    assert statuses == expected


DENIED_NO_ACTION_REQUESTS = [
    ("OPTIONS", "/auth/users/"),
    ("PUT", "/auth/users/"),
    ("PATCH", "/auth/users/"),
    ("DELETE", "/auth/users/"),
    ("OPTIONS", "/auth/users/{pk}/"),
    ("POST", "/auth/users/{pk}/"),
    ("OPTIONS", "/auth/users/{other}/"),
    ("POST", "/auth/users/{other}/"),
]


@pytest.mark.parametrize(
    "method, path",
    DENIED_NO_ACTION_REQUESTS,
    ids=request_ids(DENIED_NO_ACTION_REQUESTS),
)
def test_hide_users_keeps_403_for_denied_options_and_unmapped_methods(
    djoser_configured, regular_user, other_user, method, path
):
    """
    2.x hid denials of the list, retrieve, update and partial_update actions only.
    """
    DENIED_KEYS.update(PERMISSION_KEYS)
    with djoser_configured(PERMISSIONS=RECORDING_PERMISSIONS, HIDE_USERS=True):
        response = send(
            method, path.format(pk=regular_user.pk, other=other_user.pk), regular_user
        )
    assert response.status_code == 403


@pytest.mark.parametrize("hide_users", [True, False], ids=["hidden", "shown"])
def test_hide_users_list_filtering_follows_is_staff_not_is_superuser(
    urls_imported, regular_user, hide_users
):
    staff = User.objects.create_user(
        username="staff", email="staff@example.com", is_staff=True
    )
    superuser = User.objects.create_user(
        username="super", email="super@example.com", is_superuser=True
    )
    djoser = {**django_settings.DJOSER, "HIDE_USERS": hide_users}
    with override_settings(DJOSER=djoser):
        listed = {
            user.username: len(send("GET", "/auth/users/", user).json())
            for user in (regular_user, staff, superuser)
        }
    if hide_users:
        assert listed == {"regular": 1, "staff": 3, "super": 1}
    else:
        assert listed == {"regular": 3, "staff": 3, "super": 3}


# --- djoser's own permission classes ------------------------------------------


@pytest.mark.parametrize(
    "hide_users, denied_status", [(True, 404), (False, 403)], ids=["hidden", "shown"]
)
def test_current_user_or_admin_or_read_only_refuses_writes_to_other_users(
    djoser_configured, regular_user, other_user, hide_users, denied_status
):
    read_only = ["djoser.permissions.CurrentUserOrAdminOrReadOnly"]
    other_url = f"/auth/users/{other_user.pk}/"
    own_url = f"/auth/users/{regular_user.pk}/"
    data = '{"email": "changed@example.com"}'
    with djoser_configured(PERMISSIONS={"user": read_only}, HIDE_USERS=hide_users):
        statuses = {
            "GET other": send("GET", other_url, regular_user).status_code,
            "PUT other": send("PUT", other_url, regular_user, data).status_code,
            "PATCH other": send("PATCH", other_url, regular_user, data).status_code,
            "PATCH own": send("PATCH", own_url, regular_user, data).status_code,
        }
    assert statuses == {
        "GET other": 200,
        "PUT other": denied_status,
        "PATCH other": denied_status,
        "PATCH own": 200,
    }
    other_user.refresh_from_db()
    assert other_user.email == "other@example.com"
