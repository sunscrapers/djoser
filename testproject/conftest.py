import pytest
from rest_framework.test import APIClient
from djoser.conf import settings as djoser_settings

from testapp.factories import (
    UserFactory,
    TokenFactory,
)
from django.urls import clear_url_caches
from djoser.conf import reload_djoser_settings

Token = djoser_settings.TOKEN_MODEL


@pytest.fixture(autouse=True)
def allow_db_access(db):
    yield


@pytest.fixture
def api_client():
    """
    DRF API client fixture.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Create a basic user for testing.
    """
    return UserFactory()


@pytest.fixture
def create_superuser(db):
    """
    Create a superuser for testing.
    """
    return UserFactory.create(
        username="admin",
        email="admin@example.com",
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def inactive_user(db):
    """
    Create an inactive user for testing.
    """
    return UserFactory.create(is_active=False)


@pytest.fixture
def authenticated_client(api_client, user):
    """
    API client authenticated with a token.
    """
    token = TokenFactory.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def signal_tracker():
    """
    Track Django signals for testing.
    """

    class SignalTracker:
        def __init__(self):
            self.signal_sent = False
            self.signals_received = []

        def receiver(self, sender=None, **kwargs):
            self.signal_sent = True
            self.signals_received.append({"sender": sender, "kwargs": kwargs})

        def reset(self):
            self.signal_sent = False
            self.signals_received = []

    return SignalTracker()


@pytest.fixture(autouse=True)
def djoser_settings(settings):
    """
    Fixture to easily modify DJOSER settings in tests.

    Usage:
        def test_something(djoser_settings):
            djoser_settings["SEND_ACTIVATION_EMAIL"] = True
            djoser_settings.update(WEBAUTHN={"RP_NAME": "test"})
            # Settings are automatically applied
    """

    class DjoserSettingsProxy:
        def __init__(self, settings_dict):
            # Make a copy to avoid modifying the original
            self._settings = dict(settings_dict)
            self._original_settings = dict(settings_dict)

        def __getitem__(self, key):
            return self._settings[key]

        def __setitem__(self, key, value):
            self._settings[key] = value
            self._reload()

        def __getattr__(self, name):
            # Support attribute access like djoser_settings.EMAIL
            if name.startswith("_"):
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{name}'"
                )
            # First try to get from our custom settings
            if name in self._settings:
                return self._settings[name]
            # If not found, check the actual djoser settings object
            from djoser.conf import settings as djoser_conf_settings

            return getattr(djoser_conf_settings, name, None)

        def __setattr__(self, name, value):
            if name.startswith("_"):
                super().__setattr__(name, value)
            else:
                self._settings[name] = value
                self._reload()

        def update(self, **kwargs):
            self._settings.update(kwargs)
            self._reload()

        def get(self, key, default=None):
            return self._settings.get(key, default)

        def clear(self):
            # Reset to only default settings (not Django project settings)

            self._settings = {}
            self._reload()

        def _reload(self):
            # Update Django settings
            settings.DJOSER = self._settings
            # Force reload of djoser settings

            reload_djoser_settings(setting="DJOSER", value=self._settings)

            clear_url_caches()

    prx = DjoserSettingsProxy(settings.DJOSER)
    yield prx
    # Restore original settings
    settings.DJOSER = prx._original_settings

    reload_djoser_settings(setting="DJOSER", value=prx._original_settings)
    clear_url_caches()
