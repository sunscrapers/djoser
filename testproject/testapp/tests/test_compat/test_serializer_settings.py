"""
Pins how djoser 2.x picks and builds the serializers named in DJOSER["SERIALIZERS"].

Projects customise djoser by pointing SERIALIZERS keys, and the *_RETYPE flags that
choose between them, at their own serializers: usually subclasses of djoser's that
read ``self.context``. These tests pin which key serves each endpoint and method,
what such a serializer is given, and which keys a test suite's override_settings
reaches.

Every test in this module must pass on master unchanged. If an assertion below
disagrees with master's actual behavior, fix the TEST to pin what master does —
never the other way around.
"""

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings
from django.urls import resolve
from rest_framework.test import APIClient

User = get_user_model()

SPIES = "testapp.tests.test_compat._serializer_settings_spies"
SPY_PATHS = {
    key: f"{SPIES}.{name}"
    for key, name in {
        "activation": "ActivationSpy",
        "password_reset": "PasswordResetSpy",
        "password_reset_confirm": "PasswordResetConfirmSpy",
        "password_reset_confirm_retype": "PasswordResetConfirmRetypeSpy",
        "set_password": "SetPasswordSpy",
        "set_password_retype": "SetPasswordRetypeSpy",
        "set_username": "SetUsernameSpy",
        "set_username_retype": "SetUsernameRetypeSpy",
        "username_reset": "UsernameResetSpy",
        "username_reset_confirm": "UsernameResetConfirmSpy",
        "username_reset_confirm_retype": "UsernameResetConfirmRetypeSpy",
        "user_create": "UserCreateSpy",
        "user_create_password_retype": "UserCreatePasswordRetypeSpy",
        "user_delete": "UserDeleteSpy",
        "user": "UserSpy",
        "current_user": "CurrentUserSpy",
        "token": "TokenSpy",
        "token_create": "TokenCreateSpy",
        "provider_auth": "ProviderAuthSpy",
    }.items()
}
# 2.x reads these when its views are imported (class attributes), so only a
# DJOSER setting present at startup reaches them. It reads every other key per
# request.
IMPORT_TIME_KEYS = {"user", "token_create", "provider_auth"}
PER_REQUEST_SPY_PATHS = {
    key: path for key, path in SPY_PATHS.items() if key not in IMPORT_TIME_KEYS
}


class Endpoint(NamedTuple):
    method: str
    path: str
    # SERIALIZERS keys whose serializers 2.x builds for the request, in order.
    keys: tuple
    # view.action those serializers see on 2.x (None: the view has no action).
    action: Optional[str] = None
    # *_RETYPE flag switched on for the request.
    retype: Optional[str] = None
    anonymous: bool = False

    @property
    def flags(self):
        return {self.retype: True} if self.retype else {}

    @property
    def label(self):
        name = f"{self.method.upper()} {self.path.replace('/auth/', '', 1)}"
        return f"{name} +{self.retype}" if self.retype else name


ENDPOINTS = [
    Endpoint("post", "/auth/users/", ("user_create",), "create", anonymous=True),
    Endpoint(
        "post",
        "/auth/users/",
        ("user_create_password_retype",),
        "create",
        "USER_CREATE_PASSWORD_RETYPE",
        anonymous=True,
    ),
    Endpoint("get", "/auth/users/", ("user",), "list"),
    Endpoint("get", "/auth/users/{pk}/", ("user",), "retrieve"),
    Endpoint("put", "/auth/users/{pk}/", ("user",), "update"),
    Endpoint("patch", "/auth/users/{pk}/", ("user",), "partial_update"),
    Endpoint("delete", "/auth/users/{pk}/", ("user_delete",), "destroy"),
    Endpoint("get", "/auth/users/me/", ("current_user",), "me"),
    Endpoint("put", "/auth/users/me/", ("current_user",), "me"),
    Endpoint("patch", "/auth/users/me/", ("current_user",), "me"),
    Endpoint("delete", "/auth/users/me/", ("user_delete",), "me"),
    Endpoint(
        "post", "/auth/users/activation/", ("activation",), "activation", anonymous=True
    ),
    # 2.x serves resend_activation with the password_reset serializer.
    Endpoint(
        "post",
        "/auth/users/resend_activation/",
        ("password_reset",),
        "resend_activation",
        anonymous=True,
    ),
    Endpoint(
        "post",
        "/auth/users/reset_password/",
        ("password_reset",),
        "reset_password",
        anonymous=True,
    ),
    Endpoint(
        "post",
        "/auth/users/reset_password_confirm/",
        ("password_reset_confirm",),
        "reset_password_confirm",
        anonymous=True,
    ),
    Endpoint(
        "post",
        "/auth/users/reset_password_confirm/",
        ("password_reset_confirm_retype",),
        "reset_password_confirm",
        "PASSWORD_RESET_CONFIRM_RETYPE",
        anonymous=True,
    ),
    Endpoint("post", "/auth/users/set_password/", ("set_password",), "set_password"),
    Endpoint(
        "post",
        "/auth/users/set_password/",
        ("set_password_retype",),
        "set_password",
        "SET_PASSWORD_RETYPE",
    ),
    Endpoint("post", "/auth/users/set_username/", ("set_username",), "set_username"),
    Endpoint(
        "post",
        "/auth/users/set_username/",
        ("set_username_retype",),
        "set_username",
        "SET_USERNAME_RETYPE",
    ),
    Endpoint(
        "post",
        "/auth/users/reset_username/",
        ("username_reset",),
        "reset_username",
        anonymous=True,
    ),
    Endpoint(
        "post",
        "/auth/users/reset_username_confirm/",
        ("username_reset_confirm",),
        "reset_username_confirm",
        anonymous=True,
    ),
    Endpoint(
        "post",
        "/auth/users/reset_username_confirm/",
        ("username_reset_confirm_retype",),
        "reset_username_confirm",
        "USERNAME_RESET_CONFIRM_RETYPE",
        anonymous=True,
    ),
    # token_create validates the credentials, token renders the response.
    Endpoint("post", "/auth/token/login/", ("token_create", "token"), anonymous=True),
    Endpoint("post", "/auth/o/google-oauth2/", ("provider_auth",), anonymous=True),
]
PER_REQUEST_ENDPOINTS = [e for e in ENDPOINTS if set(e.keys) - IMPORT_TIME_KEYS]
USER_ENDPOINTS = [e for e in ENDPOINTS if e.path.startswith("/auth/users/")]


LOGIN = {"username": "spy", "password": "secret"}
NEW_EMAIL = {"email": "changed@example.com"}
NEW_USER = {"username": "new", "email": "new@example.com", "password": "Xyz-12345!"}


def _params(endpoints):
    return [pytest.param(e, id=e.label) for e in endpoints]


def _payload(endpoint):
    """
    Data that makes the view build its serializers; validation may still fail.
    """
    if endpoint.path == "/auth/token/login/":
        return LOGIN
    if endpoint.method == "delete":
        return {"current_password": "secret"}
    if endpoint.method in ("put", "patch"):
        return NEW_EMAIL
    return {}


def _send(method, path, user=None, data=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return getattr(client, method)(path, data, format="json")


def _request(endpoint, user):
    return _send(
        endpoint.method,
        endpoint.path.format(pk=user.pk),
        user=None if endpoint.anonymous else user,
        data=_payload(endpoint),
    )


@pytest.fixture
def spy_user(db):
    return User.objects.create_user(
        username="spy", email="spy@example.com", password="secret"
    )


@pytest.fixture
def seen():
    """
    The spy serializers instantiated during the test, in order.
    """
    spies = importlib.import_module(SPIES)
    spies.SEEN.clear()
    yield spies.SEEN
    spies.SEEN.clear()


@pytest.fixture
def configured_at_startup(djoser_startup_settings):
    """
    Run code as if settings.py had set SERIALIZERS (every key by default).
    """

    def configure(serializers=SPY_PATHS, **flags):
        return djoser_startup_settings(
            dict(settings.DJOSER, SERIALIZERS=serializers, **flags)
        )

    return configure


@pytest.fixture
def urlconf_loaded():
    # A project's URLconf, and with it djoser's views, is imported before a test
    # overrides settings, so override_settings is the only thing that changes.
    resolve("/auth/users/me/")


@pytest.mark.parametrize("endpoint", _params(ENDPOINTS))
def test_startup_serializers_serve_each_endpoint(
    endpoint, spy_user, seen, configured_at_startup
):
    with configured_at_startup(**endpoint.flags):
        _request(endpoint, spy_user)
    assert [serializer.spy_key for serializer in seen] == list(endpoint.keys)


@pytest.mark.parametrize("endpoint", _params(PER_REQUEST_ENDPOINTS))
def test_overridden_serializers_are_read_per_request(
    endpoint, spy_user, seen, urlconf_loaded
):
    djoser = dict(settings.DJOSER, SERIALIZERS=PER_REQUEST_SPY_PATHS, **endpoint.flags)
    with override_settings(DJOSER=djoser):
        _request(endpoint, spy_user)
    expected = [key for key in endpoint.keys if key not in IMPORT_TIME_KEYS]
    assert [serializer.spy_key for serializer in seen] == expected


@pytest.mark.parametrize("endpoint", _params(ENDPOINTS))
def test_serializer_context_holds_request_view_and_format(
    endpoint, spy_user, seen, configured_at_startup
):
    with configured_at_startup(**endpoint.flags):
        _request(endpoint, spy_user)
    # 2.x builds the token serializer of the login response without a context.
    built = [serializer for serializer in seen if serializer.spy_key != "token"]
    assert built
    for serializer in built:
        assert sorted(serializer.context) == ["format", "request", "view"]
        assert serializer.context["request"] is serializer.context["view"].request
        assert serializer.context["format"] is None


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/auth/users.json"),
        ("get", "/auth/users/{pk}.json"),
        ("get", "/auth/users/me.json"),
        ("post", "/auth/users/activation.json"),
    ],
)
def test_format_suffix_reaches_serializer_context(
    method, path, spy_user, seen, configured_at_startup
):
    with configured_at_startup():
        _send(method, path.format(pk=spy_user.pk), user=spy_user, data={})
    assert seen
    assert seen[0].context["format"] == "json"


@pytest.mark.parametrize("endpoint", _params(e for e in ENDPOINTS if e.action))
def test_serializer_sees_2x_view_action(
    endpoint, spy_user, seen, configured_at_startup
):
    with configured_at_startup(**endpoint.flags):
        _request(endpoint, spy_user)
    assert seen
    view = seen[0].context["view"]
    assert getattr(view, "action", "<no action attribute>") == endpoint.action


@pytest.mark.parametrize("endpoint", _params(USER_ENDPOINTS))
def test_serializer_view_offers_token_generator(
    endpoint, spy_user, seen, configured_at_startup
):
    # UidAndTokenSerializer and its subclasses check tokens with
    # context["view"].token_generator.
    with configured_at_startup(**endpoint.flags):
        _request(endpoint, spy_user)
    assert seen
    assert seen[0].context["view"].token_generator is default_token_generator


@pytest.mark.parametrize(
    "endpoint", _params(e for e in ENDPOINTS if e.method in ("put", "patch"))
)
def test_patch_builds_partial_serializer_and_put_does_not(
    endpoint, spy_user, seen, configured_at_startup
):
    with configured_at_startup():
        response = _request(endpoint, spy_user)
    assert response.status_code == 200
    assert [serializer.partial for serializer in seen] == [endpoint.method == "patch"]


@pytest.mark.parametrize(
    "method, path, data, status, key",
    [
        ("post", "/auth/users/", NEW_USER, 201, "user_create"),
        ("get", "/auth/users/", None, 200, "user"),
        ("get", "/auth/users/{pk}/", None, 200, "user"),
        ("put", "/auth/users/{pk}/", NEW_EMAIL, 200, "user"),
        ("patch", "/auth/users/{pk}/", NEW_EMAIL, 200, "user"),
        ("get", "/auth/users/me/", None, 200, "current_user"),
        ("put", "/auth/users/me/", NEW_EMAIL, 200, "current_user"),
        ("patch", "/auth/users/me/", NEW_EMAIL, 200, "current_user"),
        ("post", "/auth/token/login/", LOGIN, 200, "token"),
    ],
)
def test_response_body_comes_from_configured_serializer(
    method, path, data, status, key, spy_user, configured_at_startup
):
    user = spy_user if key in ("user", "current_user") else None
    with configured_at_startup():
        response = _send(method, path.format(pk=spy_user.pk), user=user, data=data)
    assert response.status_code == status
    body = response.data[0] if isinstance(response.data, list) else response.data
    assert body["marker"] == key
    if key == "user_create":
        assert "password" not in body
    if key == "token":
        assert set(body) == {"auth_token", "marker"}


@pytest.mark.parametrize("method", ["get", "put", "patch"])
@pytest.mark.parametrize("served", ["me", "by id"])
def test_view_get_object_in_serializer_returns_the_served_user(
    method, served, spy_user, configured_at_startup
):
    """
    context["view"].get_object() returns request.user on users/me/ and the user looked
    up by id on users/<id>/, here another user edited by a staff member.
    """
    other = User.objects.create_user(
        username="other", email="other@example.com", password="secret"
    )
    if served == "me":
        path, expected = "/auth/users/me/", spy_user
    else:
        spy_user.is_staff = True
        spy_user.save()
        path, expected = f"/auth/users/{other.pk}/", other
    view_object = f"{SPIES}.ViewObjectUserSerializer"
    data = None if method == "get" else NEW_EMAIL
    with configured_at_startup({"user": view_object, "current_user": view_object}):
        response = _send(method, path, user=spy_user, data=data)
    assert response.status_code == 200
    assert response.data["view_object"] == expected.pk


# The first request of a pytest-django session imports the URLconf, and with it
# djoser's views. If that request runs inside override_settings, nothing it reads
# then may outlive the override.
LEAK_DRIVER = """
import importlib
import json
import sys

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test.utils import setup_databases, setup_test_environment
from rest_framework.test import APIClient

setup_test_environment()
setup_databases(verbosity=0, interactive=False)
config = json.load(sys.stdin)
spies = importlib.import_module(config["spies"])
User = get_user_model()
imported_before = sorted(
    name
    for name in sys.modules
    if name == settings.ROOT_URLCONF or name.startswith(("djoser.views", "djoser.urls"))
)


def send(method, path, anonymous, data):
    User.objects.all().delete()
    user = User.objects.create_user(
        username="spy", email="spy@example.com", password="secret"
    )
    client = APIClient()
    if not anonymous:
        client.force_authenticate(user=user)
    spies.SEEN.clear()
    getattr(client, method)(path.format(pk=user.pk), data, format="json")
    return [serializer.spy_key for serializer in spies.SEEN]


djoser = dict(settings.DJOSER, SERIALIZERS=config["serializers"])
with override_settings(DJOSER=djoser):
    first = send("post", "/auth/users/reset_password/", True, {})
results = {
    name: send(method, path, anonymous, data)
    for name, method, path, anonymous, data in config["requests"]
}
print("RESULT " + json.dumps(
    {
        "imported_before": imported_before,
        "first": first,
        "results": results,
    }
))
"""
LEAK_ENDPOINTS = [e for e in PER_REQUEST_ENDPOINTS if not e.retype]


@pytest.fixture(scope="module")
def keys_after_override_at_first_import():
    """
    Run a fresh interpreter, where nothing has imported djoser's views yet.
    """
    testproject = Path(__file__).resolve().parents[3]
    config = {
        "spies": SPIES,
        "serializers": PER_REQUEST_SPY_PATHS,
        "requests": [
            (e.label, e.method, e.path, e.anonymous, _payload(e))
            for e in LEAK_ENDPOINTS
        ],
    }
    pythonpath = os.environ.get("PYTHONPATH", "")
    env = dict(
        os.environ,
        DJANGO_SETTINGS_MODULE=settings.SETTINGS_MODULE,
        PYTHONPATH=os.pathsep.join(
            filter(None, [str(testproject), str(testproject.parent), pythonpath])
        ),
    )
    process = subprocess.run(
        [sys.executable, "-c", LEAK_DRIVER],
        input=json.dumps(config),
        env=env,
        cwd=testproject.parent,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert process.returncode == 0, process.stderr[-3000:]
    line = next(x for x in process.stdout.splitlines() if x.startswith("RESULT "))
    outcome = json.loads(line[len("RESULT ") :])
    assert outcome["imported_before"] == []
    assert outcome["first"] == ["password_reset"]
    return outcome["results"]


@pytest.mark.parametrize("endpoint", _params(LEAK_ENDPOINTS))
def test_override_at_first_urlconf_import_does_not_stick(
    endpoint, keys_after_override_at_first_import
):
    assert keys_after_override_at_first_import[endpoint.label] == []
