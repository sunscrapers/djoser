from contextlib import contextmanager

try:
    from unittest import mock
except ImportError:
    import mock


@contextmanager
def catch_signal(signal):
    """Catch django signal and return the mocked call."""
    handler = mock.Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)
