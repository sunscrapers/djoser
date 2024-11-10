import json
import pathlib
from contextlib import suppress

import pytest
from deepdiff import DeepDiff
from django.urls import get_resolver


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
