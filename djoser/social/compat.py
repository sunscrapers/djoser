"""
Bridge the exception API change between social-auth-core < 6 and >= 6.

social-auth-core 6 replaced most specialised exception classes with a few
broad ones that carry a stable ``code`` attribute. djoser supports
social-auth-app-django 5.x (core 4.x), 6.x (core 5.x) and 7.x (core 6.x), so
the view and serializer ask this module instead of importing classes that only
exist on one side.
"""

try:
    from social_core.exceptions import MissingBackend
except ImportError:  # social-auth-core >= 6
    MissingBackend = None

try:
    from social_core.exceptions import (
        AuthMissingParameter,
        AuthStateForbidden,
        AuthStateMissing,
    )
except ImportError:  # social-auth-core >= 6
    AuthMissingParameter = AuthStateMissing = AuthStateForbidden = None

STATE_IN_REQUEST = "State could not be found in request data."
STATE_IN_SESSION = "State could not be found in server-side session data."
STATE_INVALID = "Invalid state has been provided."

# social-auth-core >= 6 reason codes raised by ``backend.validate_state()``.
_STATE_MESSAGES_BY_CODE = {
    "missing_parameter": STATE_IN_REQUEST,
    "session_context_missing": STATE_IN_SESSION,
    "state_mismatch": STATE_INVALID,
}

# social-auth-core < 6 classes raised by ``backend.validate_state()``.
_STATE_MESSAGES_BY_CLASS = [
    (AuthMissingParameter, STATE_IN_REQUEST),
    (AuthStateMissing, STATE_IN_SESSION),
    (AuthStateForbidden, STATE_INVALID),
]


def is_missing_backend(exc):
    """
    True when ``exc`` is what ``load_backend`` raises for an unknown provider.
    """
    if MissingBackend is not None and isinstance(exc, MissingBackend):
        return True
    return getattr(exc, "code", None) == "backend_missing"


def state_error_message(exc):
    """
    The djoser error message for a ``validate_state()`` failure, or None when
    ``exc`` is not one of the known state errors.
    """
    for cls, message in _STATE_MESSAGES_BY_CLASS:
        if cls is not None and isinstance(exc, cls):
            return message
    return _STATE_MESSAGES_BY_CODE.get(getattr(exc, "code", None))
