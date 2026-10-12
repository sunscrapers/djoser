"""
Pins djoser 2.x URL routing so 3.0 can prove its URLs are backwards compatible.

Covers the URL names and the paths they reverse to, what every path resolves to, URL
names derived from the user model, the include styles projects use, CSRF middleware on
every endpoint, the slash-less token and JWT URLs, the endpoints schema generators
enumerate, and a JWT-only project (TOKEN_MODEL None) that still includes
djoser.urls.authtoken.

Every test in this module must pass on master unchanged. If an assertion below disagrees
with master's actual behavior, fix the TEST to pin what master does — never the other
way around.
"""

import json
import os
import pathlib
import subprocess
import sys
from typing import NamedTuple

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.schemas.generators import EndpointEnumerator
from rest_framework.schemas.openapi import SchemaGenerator
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()

PASSWORD = "Routing-secret-1"
CREDENTIALS = {"username": "routing", "password": PASSWORD}
WRONG_CREDENTIALS = {"username": "routing", "password": "wrong"}
JSON = "application/json"
COMPAT = "testapp.tests.test_compat"
DOCUMENTED_URLCONF = f"{COMPAT}._routing_urls_documented"

# Django's startproject MIDDLEWARE, CsrfViewMiddleware included.
DJANGO_DEFAULT_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL name -> path below the include prefix, as 2.x's DefaultRouter built them.
USER_ROUTES = {
    "user-list": "users/",
    "user-me": "users/me/",
    "user-activation": "users/activation/",
    "user-resend-activation": "users/resend_activation/",
    "user-set-password": "users/set_password/",
    "user-reset-password": "users/reset_password/",
    "user-reset-password-confirm": "users/reset_password_confirm/",
    "user-set-username": "users/set_username/",
    "user-reset-username": "users/reset_username/",
    "user-reset-username-confirm": "users/reset_username_confirm/",
}
# 2.x matched these with ^token/login/?$ and ^jwt/create/?, which reverse to the
# slash-less form and serve both forms directly.
TOKEN_ROUTES = {"login": "token/login", "logout": "token/logout"}
JWT_ROUTES = {
    "jwt-create": "jwt/create",
    "jwt-refresh": "jwt/refresh",
    "jwt-verify": "jwt/verify",
}
SLASHLESS_ROUTES = {**TOKEN_ROUTES, **JWT_ROUTES}


def _suffixed(path, fmt):
    """
    The router's format-suffix route: users/ -> users.json, users/me/ -> me.json.
    """
    return f"{path.rstrip('/')}.{fmt}"


def _answer(response):
    """
    Status code and body, with freshly minted JWTs reduced to their key.
    """
    if not response.content:
        body = None
    elif response["Content-Type"].startswith(JSON):
        body = response.json()
    else:
        body = response.content.decode()
    if isinstance(body, dict):
        body = {
            key: "<jwt>" if key in ("access", "refresh") else value
            for key, value in body.items()
        }
    return response.status_code, body


def _token_auth(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {"HTTP_AUTHORIZATION": f"Token {token.key}"}


def _jwt_auth(user):
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"}


@pytest.fixture
def routing_user(db):
    return User.objects.create_user(
        username="routing", email="routing@example.com", password=PASSWORD
    )


@pytest.fixture
def token_client(routing_user):
    client = APIClient()
    client.credentials(**_token_auth(routing_user))
    return client


@pytest.fixture
def default_middleware(settings):
    """
    Django's default MIDDLEWARE, CsrfViewMiddleware included.
    """
    settings.MIDDLEWARE = DJANGO_DEFAULT_MIDDLEWARE


@pytest.fixture
def csrf_client(default_middleware):
    """
    A cookie-less API client: no CSRF cookie, CSRF checks enforced.
    """
    return Client(enforce_csrf_checks=True)


# --- URL names and paths (the testproject mounts djoser under ^auth/) --------------


@pytest.mark.parametrize(
    "name, path", [*USER_ROUTES.items(), *SLASHLESS_ROUTES.items()]
)
def test_reverse_returns_the_2x_path(name, path):
    assert reverse(name) == f"/auth/{path}"


@pytest.mark.parametrize(
    "name, kwargs, path",
    [
        ("provider-auth", {"provider": "google-oauth2"}, "/auth/o/google-oauth2/"),
        ("webauthn_signup_request", None, "/webauthn/signup_request/"),
        ("webauthn_signup", {"ukey": "abc"}, "/webauthn/signup/abc/"),
        ("webauthn_login_request", None, "/webauthn/login_request/"),
        ("webauthn_login", None, "/webauthn/login/"),
    ],
)
def test_social_and_webauthn_names_round_trip(name, kwargs, path):
    assert reverse(name, kwargs=kwargs) == path
    match = resolve(path)
    assert (match.url_name, match.kwargs) == (name, kwargs or {})


@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        ([7], None, "/auth/users/7/"),
        (None, {"id": 7}, "/auth/users/7/"),
        (["42"], None, "/auth/users/42/"),
        (["Ab9"], None, "/auth/users/Ab9/"),
        (["a@b"], None, "/auth/users/a@b/"),
        (["a+b"], None, "/auth/users/a+b/"),
        (None, {"id": "a-b_c"}, "/auth/users/a-b_c/"),
    ],
)
def test_reverse_user_detail(args, kwargs, expected):
    assert reverse("user-detail", args=args, kwargs=kwargs) == expected


@pytest.mark.parametrize(
    "args, kwargs", [(["a.b"], None), (None, {"id": "someone@example.com"})]
)
def test_reverse_user_detail_rejects_a_lookup_with_a_dot(args, kwargs):
    """
    The router's lookup regex [^/.]+ keeps dots for the format suffix.
    """
    with pytest.raises(NoReverseMatch):
        reverse("user-detail", args=args, kwargs=kwargs)


@pytest.mark.parametrize("fmt", ["json", "api"])
@pytest.mark.parametrize("name, path", USER_ROUTES.items())
def test_reverse_with_format_suffix(name, path, fmt):
    assert reverse(name, kwargs={"format": fmt}) == f"/auth/{_suffixed(path, fmt)}"


@pytest.mark.parametrize(
    "args, kwargs",
    [([7, "json"], None), (None, {"id": 7, "format": "json"})],
)
def test_reverse_user_detail_with_format_suffix(args, kwargs):
    assert reverse("user-detail", args=args, kwargs=kwargs) == "/auth/users/7.json"


@pytest.mark.parametrize(
    "name, kwargs, expected",
    [
        ("user-me", None, "/auth/users/me.json"),
        ("user-list", None, "/auth/users.json"),
        ("user-detail", {"id": 7}, "/auth/users/7.json"),
    ],
)
def test_drf_reverse_with_format(name, kwargs, expected):
    assert drf_reverse(name, kwargs=kwargs, format="json") == expected


@pytest.mark.parametrize("name", SLASHLESS_ROUTES)
def test_token_and_jwt_names_have_no_format_suffix_route(name):
    with pytest.raises(NoReverseMatch):
        reverse(name, kwargs={"format": "json"})


def _resolve_cases():
    for name, path in USER_ROUTES.items():
        yield f"/auth/{path}", name, {}
        for fmt in ("json", "api"):
            yield f"/auth/{_suffixed(path, fmt)}", name, {"format": fmt}
        yield f"/auth/{_suffixed(path, 'json')}/", name, {"format": "json"}
    for lookup in ("7", "999999", "abc", "Ab9", "a@b", "a+b", "a-b_c"):
        yield f"/auth/users/{lookup}/", "user-detail", {"id": lookup}
    yield "/auth/users/7.json", "user-detail", {"id": "7", "format": "json"}
    yield "/auth/users/7.json/", "user-detail", {"id": "7", "format": "json"}
    # A dot ends the lookup: the rest is taken as a format suffix.
    yield "/auth/users/a.b/", "user-detail", {"id": "a", "format": "b"}
    yield (
        "/auth/users/someone@example.com/",
        "user-detail",
        {"id": "someone@example", "format": "com"},
    )
    yield "/auth/users/me.xml", "user-me", {"format": "xml"}
    for name, path in SLASHLESS_ROUTES.items():
        yield f"/auth/{path}", name, {}
        yield f"/auth/{path}/", name, {}


RESOLVE_CASES = list(_resolve_cases())


@pytest.mark.parametrize(
    "path, url_name, kwargs", RESOLVE_CASES, ids=[path for path, *_ in RESOLVE_CASES]
)
def test_resolve_2x_path(path, url_name, kwargs):
    match = resolve(path)
    assert (match.url_name, match.args, match.kwargs) == (url_name, (), kwargs)


@pytest.mark.parametrize(
    "path",
    [
        "/auth/users",
        "/auth/users/me",
        "/auth/users/7",
        "/auth/users/activation",
        "/auth/users/set_password",
        "/auth/users/me.JSON",
        "/auth/users/a.b.json",
        "/auth/users/me/extra/",
        "/auth/users/7/extra/",
        "/auth/token/login.json",
        "/auth/token/login/extra",
    ],
)
def test_path_does_not_resolve(path):
    with pytest.raises(Resolver404):
        resolve(path)


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/auth/users"),
        ("post", "/auth/users"),
        ("get", "/auth/users/me"),
        ("delete", "/auth/users/me"),
        ("get", "/auth/users/{pk}"),
        ("post", "/auth/users/activation"),
        ("post", "/auth/users/set_password"),
    ],
)
def test_slashless_user_urls_answer_404(token_client, routing_user, method, path):
    """
    Only the token and JWT URLs accept a missing trailing slash.
    """
    url = path.format(pk=routing_user.pk)
    assert getattr(token_client, method)(url, {}, format="json").status_code == 404


@pytest.mark.parametrize(
    "path", ["/auth/users/me.json", "/auth/users/me.json/", "/auth/users/{pk}.json/"]
)
def test_format_suffixed_url_answers_like_the_canonical_one(
    token_client, routing_user, path
):
    canonical = token_client.get("/auth/users/me/")
    suffixed = token_client.get(path.format(pk=routing_user.pk))
    assert (suffixed.status_code, suffixed.json()) == (200, canonical.json())


@pytest.mark.parametrize(
    "path",
    [
        "/auth/users/999999/",
        "/auth/users/me.xml",
        "/auth/users/routing@example.com/",
    ],
)
def test_unknown_user_or_format_answers_404(token_client, path):
    assert token_client.get(path).status_code == 404


# --- URL names follow the user model (DRF router basename) --------------------------

TESTPROJECT_DIR = pathlib.Path(__file__).resolve().parents[3]

USER_NAME_SUFFIXES = [name.removeprefix("user-") for name in USER_ROUTES]

USER_MODEL_SCRIPT = """
import json

import django

django.setup()

from django.urls import get_resolver, resolve, reverse

names = [name for name in get_resolver().reverse_dict if isinstance(name, str)]
paths = {name: reverse(name) for name in names if not name.endswith("-detail")}
detail = [name for name in names if name.endswith("-detail")]
print(json.dumps({
    "names": sorted(names),
    "paths": paths,
    "detail": {name: reverse(name, kwargs={"id": 7}) for name in detail},
    "me": resolve("/auth/users/me/").url_name,
}))
"""


def _run_with_user_model(user_model):
    env = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": f"{COMPAT}._routing_settings_user_model",
        "ROUTING_AUTH_USER_MODEL": user_model,
        "PYTHONPATH": os.pathsep.join(
            [str(TESTPROJECT_DIR), str(TESTPROJECT_DIR.parent)]
        ),
    }
    result = subprocess.run(
        [sys.executable, "-c", USER_MODEL_SCRIPT],
        cwd=TESTPROJECT_DIR.parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.splitlines()[-1])


@pytest.mark.parametrize(
    "user_model, basename, username_field",
    [
        ("auth.User", "user", "username"),
        ("testapp.CustomUser", "customuser", "custom_username"),
        ("testapp.ExampleUser", "exampleuser", "email"),
    ],
)
def test_url_names_follow_the_user_model_class(user_model, basename, username_field):
    """
    2.x registered UserViewSet without a basename, so DRF named the routes after the
    user model class: a project whose model is CustomUser reverses 'customuser-me'.
    """
    seen = _run_with_user_model(user_model)

    user_names = [n for n in seen["names"] if n not in SLASHLESS_ROUTES]
    expected_paths = {
        f"{basename}-{suffix}": "/auth/" + path.replace("username", username_field)
        for suffix, path in zip(USER_NAME_SUFFIXES, USER_ROUTES.values())
    }
    assert {n for n in user_names if n.startswith(f"{basename}-")} == {
        *expected_paths,
        f"{basename}-detail",
    }
    if basename != "user":
        assert not [n for n in user_names if n.startswith("user-")]
    assert {
        n: p for n, p in seen["paths"].items() if n.startswith(f"{basename}-")
    } == expected_paths
    assert seen["detail"] == {f"{basename}-detail": "/auth/users/7/"}
    assert seen["me"] == f"{basename}-me"


# --- Include styles ------------------------------------------------------------------


class Style(NamedTuple):
    prefix: str
    namespaces: dict  # "user" / "token" / "jwt" -> instance namespace
    kwargs: dict  # captured by the include prefix, needed by every reverse()


def _style(module, prefix, namespaces=None, kwargs=None):
    return pytest.param(
        Style(prefix, namespaces or {}, kwargs or {}),
        marks=pytest.mark.urls(f"{COMPAT}.{module}"),
        id=module.removeprefix("_routing_urls_"),
    )


DOCUMENTED = _style("_routing_urls_documented", "/auth/")
NAMESPACED = _style(
    "_routing_urls_namespaced",
    "/api/v1/auth/",
    {"user": "djoser", "token": "djoser-token", "jwt": "djoser-jwt"},
)
PREFIXED = _style("_routing_urls_prefixed", "/api/v1/auth/")
VERSIONED = _style("_routing_urls_versioned", "/api/v2/auth/", kwargs={"version": "v2"})
ROOT = _style("_routing_urls_root", "/")
INCLUDE_STYLES = [DOCUMENTED, NAMESPACED, PREFIXED, VERSIONED, ROOT]


def _view_name(style, name):
    if name in TOKEN_ROUTES:
        group = "token"
    elif name in JWT_ROUTES:
        group = "jwt"
    else:
        group = "user"
    namespace = style.namespaces.get(group)
    return f"{namespace}:{name}" if namespace else name


def _url(style, name, **kwargs):
    return reverse(_view_name(style, name), kwargs={**style.kwargs, **kwargs})


@pytest.mark.parametrize("style", INCLUDE_STYLES)
def test_include_style_user_routes(style):
    expected = {name: style.prefix + path for name, path in USER_ROUTES.items()}
    expected["user-detail"] = f"{style.prefix}users/7/"
    reversed_paths = {name: _url(style, name) for name in USER_ROUTES}
    reversed_paths["user-detail"] = _url(style, "user-detail", id=7)
    assert reversed_paths == expected

    resolved = {name: resolve(path) for name, path in expected.items()}
    assert {name: (m.view_name, m.kwargs) for name, m in resolved.items()} == {
        name: (
            _view_name(style, name),
            {**style.kwargs, "id": "7"} if name == "user-detail" else style.kwargs,
        )
        for name in expected
    }


@pytest.mark.parametrize("style", INCLUDE_STYLES)
def test_include_style_token_and_jwt_routes(style):
    expected = {name: style.prefix + path for name, path in SLASHLESS_ROUTES.items()}
    assert {name: _url(style, name) for name in SLASHLESS_ROUTES} == expected

    resolved = {
        path: resolve(path)
        for slashless in expected.values()
        for path in (slashless, f"{slashless}/")
    }
    assert {path: (m.view_name, m.kwargs) for path, m in resolved.items()} == {
        path: (_view_name(style, name), style.kwargs)
        for name, slashless in expected.items()
        for path in (slashless, f"{slashless}/")
    }


@pytest.mark.parametrize("style", INCLUDE_STYLES)
def test_include_style_serves_requests(csrf_client, style):
    """
    A project's flow through reverse()d URLs, with Django's default middleware.
    """
    steps = []

    def post(label, name, data, **extra):
        response = csrf_client.post(_url(style, name), data, content_type=JSON, **extra)
        steps.append((label, response.status_code))
        return response

    credentials = {"username": "flow", "password": PASSWORD}
    post("register", "user-list", {**credentials, "email": "flow@example.com"})
    token = post("login", "login", credentials).json()["auth_token"]
    auth = {"HTTP_AUTHORIZATION": f"Token {token}"}
    me = csrf_client.get(_url(style, "user-me"), **auth)
    steps.append(("me", me.status_code, me.json()["username"]))
    detail = csrf_client.get(_url(style, "user-detail", id=me.json()["id"]), **auth)
    steps.append(("detail", detail.status_code, detail.json() == me.json()))
    patched = csrf_client.patch(
        _url(style, "user-me"), {"email": "new@example.com"}, content_type=JSON, **auth
    )
    steps.append(("patch me", patched.status_code, patched.json()["email"]))
    tokens = post("jwt create", "jwt-create", credentials).json()
    post("jwt refresh", "jwt-refresh", {"refresh": tokens["refresh"]})
    post("jwt verify", "jwt-verify", {"token": tokens["access"]})

    assert steps == [
        ("register", 201),
        ("login", 200),
        ("me", 200, "flow"),
        ("detail", 200, True),
        ("patch me", 200, "new@example.com"),
        ("jwt create", 200),
        ("jwt refresh", 200),
        ("jwt verify", 200),
    ]


# TokenDestroyView.post() takes no URL kwargs, so the captured-version include
# cannot serve logout on 2.x; it is left out here.
@pytest.mark.parametrize("style", [DOCUMENTED, NAMESPACED, PREFIXED, ROOT])
def test_include_style_serves_logout(csrf_client, routing_user, style):
    response = csrf_client.post(_url(style, "logout"), **_token_auth(routing_user))
    assert response.status_code == 204
    assert not Token.objects.filter(user=routing_user).exists()


@pytest.mark.urls(f"{COMPAT}._routing_urls_root")
def test_root_mount_leaves_the_project_views_alone():
    client = Client()
    assert [resolve(path).url_name for path in ("/health/", "/pages/about/")] == [
        "health",
        "about",
    ]
    assert client.get("/health/").content == b"project"
    assert client.get("/pages/about/").content == b"project"


# --- CSRF: djoser endpoints are CSRF-exempt API views --------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "/auth/users/activation/",
        "/auth/users/activation.json",
        "/auth/users/resend_activation/",
        "/auth/users/reset_password/",
        "/auth/users/reset_password_confirm/",
        "/auth/users/reset_username/",
        "/auth/users/reset_username_confirm/",
        "/auth/o/google-oauth2/",
        "/webauthn/signup_request/",
        "/webauthn/login_request/",
        "/webauthn/login/",
    ],
)
def test_anonymous_post_is_not_csrf_rejected(csrf_client, path):
    """
    API clients send no CSRF cookie; CsrfViewMiddleware must not reject them.

    POST /auth/users/ is pinned by test_urls.py.
    """
    response = csrf_client.post(path, {}, content_type=JSON)
    assert response.status_code == 400, response.content


@pytest.mark.parametrize(
    "method, path, data, expected_status",
    [
        ("post", "/auth/users/set_password/", {}, 400),
        ("post", "/auth/users/set_username/", {}, 400),
        ("put", "/auth/users/me/", {"email": "put@example.com"}, 200),
        ("patch", "/auth/users/me/", {"email": "patch@example.com"}, 200),
        ("delete", "/auth/users/me/", {"current_password": PASSWORD}, 204),
        ("put", "/auth/users/{pk}/", {"email": "put@example.com"}, 200),
        ("patch", "/auth/users/{pk}/", {"email": "patch@example.com"}, 200),
        ("delete", "/auth/users/{pk}/", {"current_password": PASSWORD}, 204),
    ],
)
def test_authenticated_write_is_not_csrf_rejected(
    csrf_client, routing_user, method, path, data, expected_status
):
    response = getattr(csrf_client, method)(
        path.format(pk=routing_user.pk),
        data,
        content_type=JSON,
        **_token_auth(routing_user),
    )
    assert response.status_code == expected_status, response.content


def _data(**fields):
    """
    Build request data, calling the values that are callables with the user.
    """

    def build(user):
        data = {k: v(user) if callable(v) else v for k, v in fields.items()}
        return data, {}

    return build


def _with_token(user):
    return {}, _token_auth(user)


TOKEN_POST_CASES = {
    # id: (route, builds (data, headers) from the user, status of the slash URL)
    "login": ("token/login", _data(**CREDENTIALS), 200),
    "login-wrong-password": ("token/login", _data(**WRONG_CREDENTIALS), 400),
    "logout": ("token/logout", _with_token, 204),
    "logout-anonymous": ("token/logout", _data(), 401),
    "jwt-create": ("jwt/create", _data(**CREDENTIALS), 200),
    "jwt-create-wrong-password": ("jwt/create", _data(**WRONG_CREDENTIALS), 401),
    "jwt-refresh": (
        "jwt/refresh",
        _data(refresh=lambda user: str(RefreshToken.for_user(user))),
        200,
    ),
    "jwt-refresh-garbage": ("jwt/refresh", _data(refresh="garbage"), 401),
    "jwt-verify": (
        "jwt/verify",
        _data(token=lambda user: str(AccessToken.for_user(user))),
        200,
    ),
    "jwt-verify-garbage": ("jwt/verify", _data(token="garbage"), 401),
}


@pytest.mark.parametrize("case", TOKEN_POST_CASES)
def test_token_and_jwt_post_is_not_csrf_rejected(csrf_client, routing_user, case):
    route, build, expected_status = TOKEN_POST_CASES[case]
    data, extra = build(routing_user)
    response = csrf_client.post(f"/auth/{route}/", data, content_type=JSON, **extra)
    assert response.status_code == expected_status, response.content


# --- Slash-less token and JWT URLs are served directly -------------------------------


@pytest.mark.parametrize("case", TOKEN_POST_CASES)
def test_slashless_post_is_served_like_the_slash_url(csrf_client, routing_user, case):
    """
    2.x served /auth/token/login and /auth/jwt/create without a redirect, also
    behind CsrfViewMiddleware for a client that has no CSRF cookie.
    """
    route, build, _ = TOKEN_POST_CASES[case]
    answers = []
    for path in (f"/auth/{route}/", f"/auth/{route}"):
        data, extra = build(routing_user)
        response = csrf_client.post(path, data, content_type=JSON, **extra)
        answers.append(_answer(response))
    slashed, slashless = answers
    assert slashless == slashed


@pytest.mark.parametrize("method", ["get", "put", "options"])
@pytest.mark.parametrize("route", SLASHLESS_ROUTES.values())
def test_slashless_url_answers_other_methods_like_the_slash_url(
    csrf_client, routing_user, route, method
):
    answers = [
        _answer(getattr(csrf_client, method)(path, **_jwt_auth(routing_user)))
        for path in (f"/auth/{route}/", f"/auth/{route}")
    ]
    slashed, slashless = answers
    assert slashless == slashed


# --- Endpoints as schema generators enumerate them -----------------------------------

DOCUMENTED_SCHEMA_COMPONENTS = {
    ("/auth/users/", "GET"): ["User"],
    ("/auth/users/", "POST"): ["UserCreate"],
    ("/auth/users/me/", "GET"): ["User"],
    ("/auth/users/me/", "PUT"): ["User"],
    ("/auth/users/me/", "PATCH"): ["User"],
    ("/auth/users/me/", "DELETE"): [],
    ("/auth/users/{id}/", "GET"): ["User"],
    ("/auth/users/{id}/", "PUT"): ["User"],
    ("/auth/users/{id}/", "PATCH"): ["User"],
    ("/auth/users/{id}/", "DELETE"): [],
    ("/auth/users/activation/", "POST"): ["Activation"],
    ("/auth/users/resend_activation/", "POST"): ["SendEmailReset"],
    ("/auth/users/reset_password/", "POST"): ["SendEmailReset"],
    ("/auth/users/reset_password_confirm/", "POST"): ["PasswordResetConfirm"],
    ("/auth/users/reset_username/", "POST"): ["SendEmailReset"],
    ("/auth/users/reset_username_confirm/", "POST"): ["UsernameResetConfirm"],
    ("/auth/users/set_password/", "POST"): ["SetPassword"],
    ("/auth/users/set_username/", "POST"): ["SetUsername"],
    ("/auth/token/login/", "POST"): ["TokenCreate"],
    ("/auth/token/logout/", "POST"): [],
    ("/auth/jwt/create/", "POST"): ["TokenObtainPair"],
    ("/auth/jwt/refresh/", "POST"): ["TokenRefresh"],
    ("/auth/jwt/verify/", "POST"): ["TokenVerify"],
}
TESTPROJECT_SCHEMA_ENDPOINTS = {
    *DOCUMENTED_SCHEMA_COMPONENTS,
    ("/auth/o/{provider}/", "GET"),
    ("/auth/o/{provider}/", "POST"),
    ("/webauthn/login/", "POST"),
    ("/webauthn/login_request/", "POST"),
    ("/webauthn/signup/{ukey}/", "POST"),
    ("/webauthn/signup_request/", "POST"),
}


def _schema_endpoints(urlconf=None):
    """
    (path, method) -> callback, as DRF, drf-spectacular and drf-yasg enumerate them.
    """
    endpoints = EndpointEnumerator(urlconf=urlconf).get_api_endpoints()
    return {(path, method): callback for path, method, callback in endpoints}


@pytest.mark.parametrize(
    "urlconf, expected",
    [
        pytest.param(None, TESTPROJECT_SCHEMA_ENDPOINTS, id="testproject"),
        pytest.param(
            DOCUMENTED_URLCONF, set(DOCUMENTED_SCHEMA_COMPONENTS), id="documented"
        ),
    ],
)
def test_schema_generators_enumerate_the_2x_endpoints(urlconf, expected):
    assert set(_schema_endpoints(urlconf)) == expected


def test_schema_generators_enumerate_no_format_suffix_route():
    paths = {path for path, _ in _schema_endpoints(DOCUMENTED_URLCONF)}
    assert [path for path in paths if "format" in path] == []


@pytest.mark.parametrize(
    "endpoint, components",
    DOCUMENTED_SCHEMA_COMPONENTS.items(),
    ids=[f"{method} {path}" for path, method in DOCUMENTED_SCHEMA_COMPONENTS],
)
def test_schema_components_build_for_endpoint(endpoint, components):
    """
    DRF's OpenAPI AutoSchema (generateschema, get_schema_view) builds every endpoint's
    components.

    uritemplate/inflection are not installed here, so this stops short of a full
    SchemaGenerator.get_schema().
    """
    callback = _schema_endpoints(DOCUMENTED_URLCONF).get(endpoint)
    assert callback is not None, f"{endpoint} is not enumerated"
    path, method = endpoint
    view = SchemaGenerator(urlconf=DOCUMENTED_URLCONF).create_view(callback, method)
    assert sorted(view.schema.get_components(path, method)) == components


# --- JWT-only project (TOKEN_MODEL None) that still includes djoser.urls.authtoken ---


@pytest.fixture
def jwt_only_project(djoser_startup_settings, settings):
    """
    DJOSER["TOKEN_MODEL"] = None in settings.py, as the docs say for JWT-only projects;
    the testproject URLconf still includes djoser.urls.authtoken.
    """
    return djoser_startup_settings({**settings.DJOSER, "TOKEN_MODEL": None})


def test_jwt_only_project_loads_the_authtoken_urls(jwt_only_project):
    names = ["login", "logout", "user-me", "jwt-create"]
    with jwt_only_project:
        reversed_paths = [reverse(name) for name in names]
    assert reversed_paths == [
        "/auth/token/login",
        "/auth/token/logout",
        "/auth/users/me/",
        "/auth/jwt/create",
    ]


@pytest.mark.parametrize(
    "method, path, data, authenticated, expected_status",
    [
        ("get", "/auth/users/me/", None, True, 200),
        ("post", "/auth/token/logout/", None, True, 204),
        ("post", "/auth/token/logout", None, True, 204),
        ("post", "/auth/token/login/", WRONG_CREDENTIALS, False, 400),
        ("post", "/auth/jwt/create/", CREDENTIALS, False, 200),
    ],
)
def test_jwt_only_project_answers_like_a_token_project(
    jwt_only_project, routing_user, method, path, data, authenticated, expected_status
):
    """
    With TOKEN_MODEL None the endpoints answer as they do with the default token model.

    A successful POST /auth/token/login/ is not pinned: 2.x raised AttributeError
    (TOKEN_MODEL.objects on None), a server error.
    """
    extra = _jwt_auth(routing_user) if authenticated else {}

    def request():
        return _answer(
            getattr(APIClient(), method)(path, data or {}, format="json", **extra)
        )

    with_token_model = request()
    with jwt_only_project:
        without_token_model = request()
    assert with_token_model[0] == expected_status
    assert without_token_model == with_token_model
