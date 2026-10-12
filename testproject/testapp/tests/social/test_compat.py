import pytest
from social_core import exceptions

from djoser.social import compat

STATE_IN_REQUEST = "State could not be found in request data."
STATE_IN_SESSION = "State could not be found in server-side session data."
STATE_INVALID = "Invalid state has been provided."


def legacy(name, *args):
    """
    Instantiate a social-auth-core < 6 exception class with the given constructor
    arguments, or skip if this core no longer ships it.
    """
    cls = getattr(exceptions, name, None)
    if cls is None:
        pytest.skip(f"social_core.exceptions.{name} not available on this core")
    return cls(*args)


def structured(code):
    """
    Model a social-auth-core >= 6 exception: a plain AuthException carrying a reason
    ``code``.

    Built this way so the branch is exercised on every core.
    """
    exc = exceptions.AuthException(None)
    exc.code = code
    return exc


@pytest.mark.parametrize(
    "name, args, expected",
    [
        ("AuthMissingParameter", (None, "state"), STATE_IN_REQUEST),
        ("AuthStateMissing", (None, "state"), STATE_IN_SESSION),
        ("AuthStateForbidden", (None,), STATE_INVALID),
    ],
)
def test_state_error_message_maps_legacy_classes(name, args, expected):
    assert compat.state_error_message(legacy(name, *args)) == expected


@pytest.mark.parametrize(
    "code, expected",
    [
        ("missing_parameter", STATE_IN_REQUEST),
        ("session_context_missing", STATE_IN_SESSION),
        ("state_mismatch", STATE_INVALID),
    ],
)
def test_state_error_message_maps_structured_codes(code, expected):
    assert compat.state_error_message(structured(code)) == expected


def test_state_error_message_is_none_for_other_errors():
    assert compat.state_error_message(exceptions.AuthCanceled(None)) is None
    assert compat.state_error_message(structured("nonce_mismatch")) is None


def test_is_missing_backend_for_legacy_class():
    assert compat.is_missing_backend(legacy("MissingBackend", "nope")) is True


def test_is_missing_backend_for_structured_code():
    exc = exceptions.SocialAuthBaseException(None)
    exc.code = "backend_missing"
    assert compat.is_missing_backend(exc) is True


def test_is_missing_backend_is_false_for_other_errors():
    assert compat.is_missing_backend(exceptions.AuthCanceled(None)) is False
    assert compat.is_missing_backend(structured("invalid_setting")) is False
