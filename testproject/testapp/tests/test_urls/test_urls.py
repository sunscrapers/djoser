import json
import pathlib
from contextlib import suppress

import pytest
from deepdiff import DeepDiff
from django.test import Client
from django.urls import get_resolver, resolve
from django.http import HttpResponseNotAllowed
from django.test import RequestFactory
from rest_framework.views import APIView


@pytest.mark.parametrize(
    "path",
    ["/auth/users/", "/auth/users/me/", "/auth/users/1/"],
)
def test_dispatcher_routed_urls_are_csrf_exempt(path):
    """
    CsrfViewMiddleware inspects the callable the resolver returns.

    The dispatcher wraps the view, so it has to carry csrf_exempt itself or CSRF gets
    enforced on endpoints that DRF exempts.
    """
    assert getattr(resolve(path).func, "csrf_exempt", False) is True


@pytest.mark.django_db
def test_registration_works_with_csrf_middleware_enabled(settings):
    """
    Django's default MIDDLEWARE includes CsrfViewMiddleware.

    An API client has no CSRF cookie, so registration must not be rejected by it.
    """
    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
    ]
    response = Client(enforce_csrf_checks=True).post(
        "/auth/users/",
        {
            "username": "csrfuser",
            "password": "testing123!",
            "email": "csrf@example.com",
        },
        content_type="application/json",
    )
    assert response.status_code == 201, response.content


def test_create_dispatcher_not_allowed():
    from djoser.urls.utils import create_dispatcher

    class DummyView(APIView):
        def get(self, request):
            return "response"

    method_view_map = {"GET": DummyView}
    dispatcher = create_dispatcher(method_view_map)

    factory = RequestFactory()
    request = factory.post("/")

    response = dispatcher(request)
    assert isinstance(response, HttpResponseNotAllowed)
    assert "GET" in response["Allow"]


@pytest.mark.django_db
def test_urls_have_not_changed(settings):
    BASE_DIR = settings.BASE_DIR
    if isinstance(BASE_DIR, str):
        BASE_DIR = pathlib.Path(BASE_DIR)
    TEST_PATH = BASE_DIR / "testapp" / "tests" / "test_urls"
    FILE_PATH = TEST_PATH / "urls_snapshot.json"
    url_patterns = get_resolver().url_patterns

    def get_all_urls(patterns, prefix=""):
        urls = []
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                urls += get_all_urls(
                    pattern.url_patterns,
                    prefix + pattern.pattern.regex.pattern,
                )
            else:
                pattern_str = prefix + pattern.pattern.regex.pattern
                name = pattern.name if pattern.name else None
                allowed_methods = []
                if hasattr(pattern, "callback"):
                    view = pattern.callback
                    if hasattr(view, "http_method_names"):
                        allowed_methods = view.http_method_names
                    elif hasattr(view, "actions"):
                        allowed_methods = list(view.actions.keys())
                    elif hasattr(
                        view, "view_class"
                    ):  # assume all, even though probably not
                        allowed_methods = view.view_class.http_method_names
                    elif (
                        hasattr(view, "__name__")
                        and view.__name__ == "dispatcher"
                        and hasattr(view, "_allowed_methods")
                    ):
                        allowed_methods = [
                            method.lower() for method in view._allowed_methods
                        ]
                    else:
                        raise NotImplementedError(
                            "Function based views are not supported"
                        )

                # head is not present in the CI for some reason...
                with suppress(ValueError):
                    i = allowed_methods.index("head")
                    del allowed_methods[i]

                urls.append(
                    {
                        "pattern": pattern_str,
                        "name": name,
                        "allowed_methods": allowed_methods,
                    }
                )
        return urls

    current_urls = sorted(get_all_urls(url_patterns), key=lambda x: x["pattern"])
    # api-root generates different regex pattern locally vs in CI
    current_urls = [el for el in current_urls if el["name"] != "api-root"]

    if not FILE_PATH.exists():
        with open(FILE_PATH, "w") as f:
            json.dump(current_urls, f, indent=2)
        pytest.fail(
            "URL snapshot not found. Created snapshot with current URLs. Re-run the test."  # noqa: E501
        )

    with open(FILE_PATH) as f:
        saved_urls = json.load(f)

    diff = DeepDiff(current_urls, saved_urls)
    if diff:
        with open(FILE_PATH, "w") as f:
            json.dump(current_urls, f, indent=2)
        pytest.fail(
            f"URL structure has changed. Updated snapshot with new URLs and names. Diff:\n\n{diff}"  # noqa: E501
        )


@pytest.mark.parametrize(
    "path,expected_kwargs",
    [
        ("/auth/users/1.json", {"id": "1", "format": "json"}),
        ("/auth/users.json", {"format": "json"}),
        ("/auth/users/1/", {"id": "1"}),
    ],
)
def test_format_suffix_routes_resolve(path, expected_kwargs):
    """
    DRF's DefaultRouter generated these before the URLs were hand-written.
    """
    assert resolve(path).kwargs == expected_kwargs


def test_user_lookup_does_not_swallow_dots():
    """
    A dotted segment must be read as a format suffix, not as the lookup value.
    """
    assert resolve("/auth/users/1.json").kwargs["id"] == "1"


@pytest.mark.parametrize(
    "path",
    ["/auth/token/login", "/auth/token/logout", "/auth/jwt/create", "/auth/jwt/verify"],
)
@pytest.mark.django_db
def test_slashless_token_urls_redirect_preserving_method(path):
    """
    Djoser 2.x matched these with an optional trailing slash.

    A 308 is used rather than a 301 so clients repeat the POST with its body instead of
    downgrading to GET.
    """
    response = Client().post(path, {}, content_type="application/json")
    assert response.status_code == 308
    assert response["Location"] == f"{path}/"
