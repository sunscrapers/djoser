"""
Pins djoser 2.x behaviour for every HTTP method on every djoser URL, per auth state.

With default settings, each djoser endpoint and its format-suffix variants answer GET,
HEAD, POST, PUT, PATCH, DELETE, OPTIONS and TRACE from anonymous, regular and staff
clients with a fixed status code, error body (detail and code) and WWW-Authenticate
header, and every 405 carries an Allow header listing all methods of the path. 3.0
replaced the viewset and router with one view per endpoint behind method dispatchers;
these tests hold the URLs to what 2.x clients see.

Every test in this module must pass on master unchanged. If an assertion below disagrees
with master's actual behavior, fix the TEST to pin what master does — never the other
way around.

Cells whose status code another master test already pins are left out of the matrices
(see PINNED_ELSEWHERE). Not pinned here: OPTIONS metadata bodies, the browsable API, the
Allow header on responses other than 405, HEAD and OPTIONS on /users/me/ (500 on 2.x),
slash-less token and JWT URLs, the /auth/ API root and customised PERMISSIONS.
"""

import pytest
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.views import APIView, exception_handler
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

METHODS = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]
NOT_POST = [method for method in METHODS if method != "POST"]
UNMAPPED_ON_POST_ONLY = ["GET", "HEAD", "PUT", "PATCH", "DELETE", "TRACE"]
UNSAFE_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
AUTHENTICATED = ["user", "staff", "jwt user"]
MISSING_PK = 999999

LIST_ALLOW = "GET, POST, HEAD, OPTIONS"
INSTANCE_ALLOW = "GET, PUT, PATCH, DELETE, HEAD, OPTIONS"
POST_ALLOW = "POST, OPTIONS"

NOT_AUTHENTICATED = (
    "Authentication credentials were not provided.",
    "not_authenticated",
)
PERMISSION_DENIED = (
    "You do not have permission to perform this action.",
    "permission_denied",
)
CSRF_FAILED = ("CSRF Failed: CSRF cookie not set.", "permission_denied")
NOT_FOUND = ("Not found.", "not_found")
# get_object_or_404's Http404 for a missing user. DRF 3.15+ passes its message
# through, older DRF answers "Not found.", so ask DRF instead of hard-coding either.
_missing_user_detail = exception_handler(
    Http404("No User matches the given query."), {}
).data["detail"]
NO_SUCH_USER = (str(_missing_user_detail), "not_found")
NOT_ACCEPTABLE = ("Could not satisfy the request Accept header.", "not_acceptable")
BEARER_CHALLENGE = 'Bearer realm="api"'

PUBLIC_ACTIONS = [
    "activation",
    "resend_activation",
    "reset_password",
    "reset_password_confirm",
    "reset_username",
    "reset_username_confirm",
]
PRIVATE_ACTIONS = ["set_password", "set_username"]
FORMAT_SUFFIXES = [".json", ".json/"]


def _variants(stem):
    """
    The canonical URL of a router route followed by its format-suffix forms.
    """
    return [f"{stem}/", *(f"{stem}{suffix}" for suffix in FORMAT_SUFFIXES)]


# Paths are templates: {user}, {staff} and {missing} become primary keys.
USER_LIST = _variants("/auth/users")
ME = _variants("/auth/users/me")
DETAIL = [*_variants("/auth/users/{user}"), "/auth/users/{staff}/"]
MISSING = ["/auth/users/{missing}/", "/auth/users/{missing}.json"]
PUBLIC_POST = [path for a in PUBLIC_ACTIONS for path in _variants(f"/auth/users/{a}")]
PRIVATE_POST = [path for a in PRIVATE_ACTIONS for path in _variants(f"/auth/users/{a}")]
TOKEN_LOGIN = "/auth/token/login/"
TOKEN_LOGOUT = "/auth/token/logout/"
JWT = ["/auth/jwt/create/", "/auth/jwt/refresh/", "/auth/jwt/verify/"]

# (client, method, path) cells whose status code master already pins in
# test_urls/test_method_parity.py, test_user_list.py, test_user_detail.py,
# test_user_view.py or test_token_destroy.py.
PINNED_ELSEWHERE = {
    ("anonymous", "GET", "/auth/users/"),
    ("anonymous", "PUT", "/auth/users/"),
    ("anonymous", "OPTIONS", "/auth/users/"),
    ("anonymous", "GET", "/auth/users/{user}/"),
    ("anonymous", "POST", TOKEN_LOGOUT),
    ("user", "PUT", "/auth/users/"),
    ("user", "OPTIONS", "/auth/users/"),
    ("user", "OPTIONS", "/auth/users/activation/"),
    ("user", "OPTIONS", "/auth/users/reset_password/"),
    ("user", "OPTIONS", "/auth/users/{user}/"),
    ("user", "OPTIONS", TOKEN_LOGOUT),
    ("user", "GET", "/auth/users/{staff}/"),
    ("user", "PUT", "/auth/users/{staff}/"),
    ("user", "PATCH", "/auth/users/{staff}/"),
}


def _cells(clients, methods, paths, *extra):
    """
    Every (client, method, path, *extra) combination not pinned elsewhere.
    """
    return [
        (who, method, path, *extra)
        for who in clients
        for method in methods
        for path in paths
        if (who, method, path) not in PINNED_ELSEWHERE
    ]


def _anonymous_cells(methods, paths):
    return [cell[1:] for cell in _cells(["anonymous"], methods, paths)]


def _allow(path):
    """
    The Allow header 2.x sends on a 405 from the canonical djoser ``path``.
    """
    if path == "/auth/users/":
        return LIST_ALLOW
    if path in ("/auth/users/me/", "/auth/users/{user}/"):
        return INSTANCE_ALLOW
    return POST_ALLOW


def _error(response):
    detail = response.data["detail"]
    return str(detail), detail.code


def _error_codes(response):
    return {
        field: [error.code for error in errors]
        for field, errors in response.data.items()
    }


def _request(client, method, path, **extra):
    """
    Send ``method`` with an empty JSON body, the way an API client probes a URL.
    """
    return client.generic(method, path, "{}", content_type="application/json", **extra)


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="regular", email="regular@example.com")


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff", email="staff@example.com", is_staff=True
    )


@pytest.fixture
def url(regular_user, staff_user):
    def build(template):
        return template.format(
            user=regular_user.pk, staff=staff_user.pk, missing=MISSING_PK
        )

    return build


@pytest.fixture
def client_as(regular_user, staff_user):
    """
    Build an API client for "anonymous", "user" or "staff" (DRF token authentication),
    or "jwt user" (a simplejwt access token for the regular user).
    """

    def build(who):
        client = APIClient()
        if who in ("user", "staff"):
            token = Token.objects.create(
                user=regular_user if who == "user" else staff_user
            )
            client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        elif who == "jwt user":
            access = RefreshToken.for_user(regular_user).access_token
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return client

    return build


# --- 405: methods a path does not serve --------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "who, method, path, allow",
    [
        *_cells(
            AUTHENTICATED, ["PUT", "PATCH", "DELETE", "TRACE"], USER_LIST, LIST_ALLOW
        ),
        *_cells(
            AUTHENTICATED, ["POST", "TRACE"], ME + DETAIL + MISSING, INSTANCE_ALLOW
        ),
        *_cells(
            AUTHENTICATED,
            UNMAPPED_ON_POST_ONLY,
            [*PUBLIC_POST, *PRIVATE_POST, TOKEN_LOGIN, TOKEN_LOGOUT, *JWT],
            POST_ALLOW,
        ),
        # The login endpoints authenticate nobody, so anonymous clients get the 405.
        *_cells(["anonymous"], UNMAPPED_ON_POST_ONLY, [TOKEN_LOGIN, *JWT], POST_ALLOW),
    ],
)
def test_unmapped_method_gets_json_405_with_the_path_allow_header(
    client_as, url, who, method, path, allow
):
    response = _request(client_as(who), method, url(path))
    assert response.status_code == 405
    assert response["Allow"] == allow
    assert response["Content-Type"] == "application/json"
    assert _error(response) == (f'Method "{method}" not allowed.', "method_not_allowed")


# --- 401: authentication runs before the method, object and body checks -----------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, path",
    [
        *_anonymous_cells(NOT_POST, USER_LIST),
        *_anonymous_cells(
            METHODS, [*ME, *DETAIL, *MISSING, *PRIVATE_POST, TOKEN_LOGOUT]
        ),
    ],
)
def test_anonymous_request_to_authenticated_endpoint_gets_401(url, method, path):
    response = _request(APIClient(), method, url(path))
    assert response.status_code == 401
    assert _error(response) == NOT_AUTHENTICATED
    assert response["WWW-Authenticate"] == BEARER_CHALLENGE


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, path", _anonymous_cells(UNMAPPED_ON_POST_ONLY, PUBLIC_POST)
)
def test_anonymous_unmapped_method_on_public_post_endpoint_gets_401(method, path):
    """
    2.x checked methods a viewset action does not map against PERMISSIONS.user
    (CurrentUserOrAdmin), so anonymous clients got 401 before the 405.
    """
    response = _request(APIClient(), method, path)
    assert response.status_code == 401
    assert _error(response) == NOT_AUTHENTICATED
    assert response["WWW-Authenticate"] == BEARER_CHALLENGE


@pytest.mark.django_db
@pytest.mark.parametrize("path", PUBLIC_POST)
def test_anonymous_options_on_public_post_endpoint_gets_401(path):
    """
    OPTIONS, the viewset's metadata action, was checked against PERMISSIONS.user.
    """
    response = _request(APIClient(), "OPTIONS", path)
    assert response.status_code == 401
    assert _error(response) == NOT_AUTHENTICATED
    assert response["WWW-Authenticate"] == BEARER_CHALLENGE


# --- OPTIONS once authentication passes --------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "who, method, path",
    [
        *_cells(
            AUTHENTICATED,
            ["OPTIONS"],
            [
                *USER_LIST,
                *DETAIL,
                *MISSING,
                *PUBLIC_POST,
                *PRIVATE_POST,
                TOKEN_LOGIN,
                TOKEN_LOGOUT,
                *JWT,
            ],
        ),
        *_cells(["anonymous"], ["OPTIONS"], [TOKEN_LOGIN, *JWT]),
    ],
)
def test_options_gets_200_once_authentication_passes(client_as, url, who, method, path):
    assert _request(client_as(who), method, url(path)).status_code == 200


# --- /users/<id>/: 401, then 404 for hidden or missing users, 403 on DELETE --------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "who, method, path, status, error",
    [
        # HIDE_USERS (default True) turns a denied request for another user into 404 ...
        *_cells(
            ["user", "jwt user"],
            ["GET", "HEAD", "PUT", "PATCH"],
            ["/auth/users/{staff}/", "/auth/users/{staff}.json"],
            404,
            NOT_FOUND,
        ),
        # ... except DELETE, which 2.x left out of the conversion.
        *_cells(
            ["user", "jwt user"],
            ["DELETE"],
            ["/auth/users/{staff}/", "/auth/users/{staff}.json"],
            403,
            PERMISSION_DENIED,
        ),
        *_cells(
            AUTHENTICATED,
            ["GET", "HEAD", "PUT", "PATCH", "DELETE"],
            MISSING,
            404,
            NO_SUCH_USER,
        ),
    ],
)
def test_user_detail_errors_for_other_and_missing_users(
    client_as, url, who, method, path, status, error
):
    response = _request(client_as(who), method, url(path))
    assert response.status_code == status
    assert _error(response) == error


# --- format suffixes and content negotiation ---------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("suffix", FORMAT_SUFFIXES)
@pytest.mark.parametrize(
    "who, method, stem, status",
    [
        ("user", "GET", "/auth/users", 200),
        ("staff", "GET", "/auth/users", 200),
        ("anonymous", "POST", "/auth/users", 400),
        *(
            ("user", method, stem, status)
            for stem in ("/auth/users/me", "/auth/users/{user}")
            for method, status in [
                ("GET", 200),
                ("PUT", 200),
                ("PATCH", 200),
                ("DELETE", 400),
            ]
        ),
        ("staff", "GET", "/auth/users/{user}", 200),
        *(("anonymous", "POST", f"/auth/users/{a}", 400) for a in PUBLIC_ACTIONS),
        *(("user", "POST", f"/auth/users/{a}", 400) for a in PRIVATE_ACTIONS),
    ],
)
def test_format_suffix_route_answers_like_the_canonical_url(
    client_as, url, who, method, stem, status, suffix
):
    client = client_as(who)
    canonical = _request(client, method, url(f"{stem}/"))
    suffixed = _request(client, method, url(f"{stem}{suffix}"))
    assert canonical.status_code == status
    assert (suffixed.status_code, suffixed.data) == (status, canonical.data)


@pytest.mark.django_db
@pytest.mark.parametrize("who", ["anonymous", "user"])
@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/auth/users.xml"),
        ("GET", "/auth/users/me.xml"),
        ("GET", "/auth/users/{user}.xml"),
        ("GET", "/auth/users/me/?format=xml"),
        ("POST", "/auth/users/activation.xml"),
        ("PUT", "/auth/users/activation.xml"),
        ("POST", "/auth/users/set_password.xml"),
    ],
)
def test_unknown_format_gets_404_before_authentication(
    client_as, url, who, method, path
):
    response = _request(client_as(who), method, url(path))
    assert response.status_code == 404
    assert _error(response) == NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("who", ["anonymous", "user"])
@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/auth/users/"),
        ("GET", "/auth/users/me/"),
        ("GET", "/auth/users/{user}/"),
        ("POST", "/auth/users/activation/"),
        ("PUT", "/auth/users/activation/"),
        ("POST", "/auth/users/set_password/"),
        ("POST", TOKEN_LOGIN),
        ("POST", TOKEN_LOGOUT),
        ("POST", "/auth/jwt/create/"),
    ],
)
def test_unsupported_accept_header_gets_406_before_authentication(
    client_as, url, who, method, path
):
    response = _request(
        client_as(who), method, url(path), HTTP_ACCEPT="application/xml"
    )
    assert response.status_code == 406
    assert _error(response) == NOT_ACCEPTABLE


# --- 400 for an empty body ------------------------------------------------------------

PUBLIC_EMPTY_BODY_ERRORS = [
    ("POST", "/auth/users/", {"password": ["required"], "username": ["required"]}),
    ("POST", "/auth/users/activation/", {"token": ["required"], "uid": ["required"]}),
    ("POST", "/auth/users/resend_activation/", {"email": ["required"]}),
    ("POST", "/auth/users/reset_password/", {"email": ["required"]}),
    (
        "POST",
        "/auth/users/reset_password_confirm/",
        {"new_password": ["required"], "token": ["required"], "uid": ["required"]},
    ),
    ("POST", "/auth/users/reset_username/", {"email": ["required"]}),
    ("POST", "/auth/users/reset_username_confirm/", {"new_username": ["required"]}),
    ("POST", "/auth/jwt/create/", {"password": ["required"], "username": ["required"]}),
    ("POST", "/auth/jwt/refresh/", {"refresh": ["required"]}),
    ("POST", "/auth/jwt/verify/", {"token": ["required"]}),
]
PRIVATE_EMPTY_BODY_ERRORS = [
    (
        "POST",
        "/auth/users/set_password/",
        {"current_password": ["required"], "new_password": ["required"]},
    ),
    (
        "POST",
        "/auth/users/set_username/",
        {"current_password": ["required"], "new_username": ["required"]},
    ),
    ("DELETE", "/auth/users/me/", {"current_password": ["required"]}),
    ("DELETE", "/auth/users/{user}/", {"current_password": ["required"]}),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "who, method, path, errors",
    [
        *(
            (who, *cell)
            for who in ("anonymous", "user")
            for cell in PUBLIC_EMPTY_BODY_ERRORS
        ),
        *((who, *cell) for who in AUTHENTICATED for cell in PRIVATE_EMPTY_BODY_ERRORS),
    ],
)
def test_empty_body_gets_400_with_required_field_codes(
    client_as, url, who, method, path, errors
):
    response = _request(client_as(who), method, url(path))
    assert response.status_code == 400
    assert _error_codes(response) == errors


# --- SessionAuthentication and CSRF ---------------------------------------------------

SESSION_FIRST = [SessionAuthentication, TokenAuthentication]
CSRF_SECRET = "abcdefghijklmnopqrstuvwxyzABCDEF"
SESSION_PATHS = [
    "/auth/users/",
    "/auth/users/me/",
    "/auth/users/{user}/",
    *(f"/auth/users/{a}/" for a in PUBLIC_ACTIONS + PRIVATE_ACTIONS),
    TOKEN_LOGIN,
    TOKEN_LOGOUT,
]


@pytest.fixture
def session_client(settings, monkeypatch, regular_user):
    """
    Build clients for a project that lists SessionAuthentication first in settings.py
    and keeps Django's CsrfViewMiddleware: "anonymous", "session user" (logged in, no
    CSRF token) or "session user with csrf".

    DRF copies DEFAULT_AUTHENTICATION_CLASSES onto APIView when rest_framework.views is
    imported, so overriding REST_FRAMEWORK alone never reaches the views; the class
    attribute is patched to what that startup setting would have made it.
    """
    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_AUTHENTICATION_CLASSES": [
            f"{cls.__module__}.{cls.__qualname__}" for cls in SESSION_FIRST
        ],
    }
    monkeypatch.setattr(APIView, "authentication_classes", SESSION_FIRST)

    def build(who):
        client = APIClient(enforce_csrf_checks=True)
        if who != "anonymous":
            client.force_login(regular_user)
        if who == "session user with csrf":
            client.cookies["csrftoken"] = CSRF_SECRET
            client.credentials(HTTP_X_CSRFTOKEN=CSRF_SECRET)
        return client

    return build


@pytest.mark.django_db
@pytest.mark.parametrize("method", UNSAFE_METHODS)
@pytest.mark.parametrize("path", SESSION_PATHS)
def test_session_user_without_csrf_token_gets_403_on_unsafe_methods(
    session_client, url, method, path
):
    response = _request(session_client("session user"), method, url(path))
    assert response.status_code == 403
    assert _error(response) == CSRF_FAILED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, path, status",
    [
        ("GET", "/auth/users/", 200),
        ("GET", "/auth/users/me/", 200),
        ("GET", "/auth/users/{user}/", 200),
        *(("GET", f"/auth/users/{a}/", 405) for a in PUBLIC_ACTIONS + PRIVATE_ACTIONS),
        *(
            ("OPTIONS", f"/auth/users/{a}/", 200)
            for a in PUBLIC_ACTIONS + PRIVATE_ACTIONS
        ),
        *(("TRACE", path, 405) for path in SESSION_PATHS),
    ],
)
def test_session_user_without_csrf_token_is_served_safe_methods(
    session_client, url, method, path, status
):
    response = _request(session_client("session user"), method, url(path))
    assert response.status_code == status
    if status == 405:
        assert response["Allow"] == _allow(path)


@pytest.mark.django_db
@pytest.mark.parametrize("path", JWT)
def test_simplejwt_endpoints_do_not_check_csrf_for_session_users(session_client, path):
    """
    Simplejwt views authenticate nobody, so a logged-in browser gets no CSRF 403.
    """
    response = _request(session_client("session user"), "POST", path)
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, path, status",
    [
        ("POST", "/auth/users/", 400),
        *((method, "/auth/users/", 405) for method in ["PUT", "PATCH", "DELETE"]),
        ("PUT", "/auth/users/me/", 200),
        ("PATCH", "/auth/users/me/", 200),
        ("DELETE", "/auth/users/me/", 400),
        ("POST", "/auth/users/me/", 405),
        ("PUT", "/auth/users/{user}/", 200),
        ("PATCH", "/auth/users/{user}/", 200),
        ("DELETE", "/auth/users/{user}/", 400),
        ("POST", "/auth/users/{user}/", 405),
        *(("POST", f"/auth/users/{a}/", 400) for a in PUBLIC_ACTIONS + PRIVATE_ACTIONS),
        *(("PUT", f"/auth/users/{a}/", 405) for a in PUBLIC_ACTIONS + PRIVATE_ACTIONS),
        ("POST", TOKEN_LOGIN, 400),
        ("PUT", TOKEN_LOGIN, 405),
        ("POST", TOKEN_LOGOUT, 204),
        ("PUT", TOKEN_LOGOUT, 405),
    ],
)
def test_session_user_with_csrf_token_reaches_the_endpoint(
    session_client, url, method, path, status
):
    response = _request(session_client("session user with csrf"), method, url(path))
    assert response.status_code == status
    if status == 405:
        assert response["Allow"] == _allow(path)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, path",
    [
        *((method, "/auth/users/") for method in NOT_POST),
        *(
            (method, path)
            for method in METHODS
            for path in [
                "/auth/users/me/",
                "/auth/users/{user}/",
                "/auth/users/{missing}/",
                "/auth/users/set_password/",
                "/auth/users/set_username/",
                TOKEN_LOGOUT,
            ]
        ),
    ],
)
def test_session_first_anonymous_request_gets_403_not_authenticated(
    session_client, url, method, path
):
    """
    SessionAuthentication sends no challenge, so DRF answers 403 instead of 401.
    """
    response = _request(session_client("anonymous"), method, url(path))
    assert response.status_code == 403
    assert _error(response) == NOT_AUTHENTICATED
    assert not response.has_header("WWW-Authenticate")


@pytest.mark.django_db
@pytest.mark.parametrize("method", [*UNMAPPED_ON_POST_ONLY, "OPTIONS"])
@pytest.mark.parametrize("path", [f"/auth/users/{a}/" for a in PUBLIC_ACTIONS])
def test_session_first_anonymous_unmapped_method_on_public_post_endpoint_gets_403(
    session_client, method, path
):
    """
    The PERMISSIONS.user check above, answered the SessionAuthentication way.
    """
    response = _request(session_client("anonymous"), method, path)
    assert response.status_code == 403
    assert _error(response) == NOT_AUTHENTICATED
    assert not response.has_header("WWW-Authenticate")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    ["/auth/users/", *(f"/auth/users/{a}/" for a in PUBLIC_ACTIONS), TOKEN_LOGIN],
)
def test_session_first_anonymous_post_to_public_endpoint_skips_csrf(
    session_client, path
):
    """Without a session there is nothing to check CSRF for: the body is validated."""
    response = _request(session_client("anonymous"), "POST", path)
    assert response.status_code == 400
