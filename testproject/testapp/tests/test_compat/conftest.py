"""
Fixtures for the 2.x -> 3.0 compatibility tests.

Everything in this package must pass unchanged on master (2.x) and on 3.0.
"""

import importlib
import sys
from contextlib import contextmanager

import pytest
from django.conf import settings as django_settings
from django.test import override_settings
from django.urls import clear_url_caches
from django.urls import converters as url_converters

from djoser import conf as djoser_conf

# Modules (and their submodules) that read DJOSER settings while being imported,
# e.g. ``permission_classes = settings.PERMISSIONS.user_create`` or a URL module
# picking its views. ROOT_URLCONF is added at runtime.
STARTUP_MODULES = (
    "djoser.views",
    "djoser.urls",
    "djoser.social.views",
    "djoser.social.urls",
    "djoser.webauthn.views",
    "djoser.webauthn.urls",
)


def _pop_modules(prefixes):
    """
    Remove matching modules from sys.modules and from their parent packages.

    Dropping the parent attribute too makes ``from djoser import views`` import the
    module again instead of returning the one still bound on the package.
    """
    submodule_prefixes = tuple(f"{prefix}." for prefix in prefixes)
    popped = {
        name: sys.modules.pop(name)
        for name in list(sys.modules)
        if name in prefixes or name.startswith(submodule_prefixes)
    }
    for name, module in popped.items():
        parent, _, child = name.rpartition(".")
        if getattr(sys.modules.get(parent), child, None) is module:
            delattr(sys.modules[parent], child)
    return popped


def _put_modules(modules):
    sys.modules.update(modules)
    for name, module in modules.items():
        parent, _, child = name.rpartition(".")
        if parent in sys.modules:
            setattr(sys.modules[parent], child, module)


def _as_import_path(value, modules):
    """
    Turn a class djoser.conf cached from one of ``modules`` back into its path.
    """
    if isinstance(value, (list, tuple)):
        return [_as_import_path(item, modules) for item in value]
    if isinstance(value, type) and value.__module__ in modules:
        return f"{value.__module__}.{value.__qualname__}"
    return value


@contextmanager
def _startup_settings(djoser, modules=()):
    root_urlconf = django_settings.ROOT_URLCONF
    prefixes = (*STARTUP_MODULES, root_urlconf, *modules)
    # Load whatever the project loads at startup under its own settings first, so
    # only the modules matched by ``prefixes`` get imported with ``djoser``.
    importlib.import_module(root_urlconf)
    defaults = dict(djoser_conf.default_settings)
    converters = dict(url_converters.REGISTERED_CONVERTERS)
    with override_settings(DJOSER=djoser):
        originals = _pop_modules(prefixes)
        try:
            # djoser.conf caches imported classes in its default dicts (3.0's VIEWS
            # holds the old view classes); use fresh copies that import them again.
            djoser_conf.default_settings.update(
                {
                    name: djoser_conf.ObjDict(
                        {
                            key: _as_import_path(value, originals)
                            for key, value in group.items()
                        }
                    )
                    for name, group in defaults.items()
                    if isinstance(group, dict)
                }
            )
            djoser_conf.reload_djoser_settings(setting="DJOSER", value=djoser)
            # Registering a converter name twice warns on Django 5.x, fails on 6.0.
            for name, converter in converters.items():
                if type(converter).__module__ in originals:
                    del url_converters.REGISTERED_CONVERTERS[name]
            clear_url_caches()
            importlib.import_module(root_urlconf)
            yield
        finally:
            _pop_modules(prefixes)
            _put_modules(originals)
            djoser_conf.default_settings.update(defaults)
            url_converters.REGISTERED_CONVERTERS.clear()
            url_converters.REGISTERED_CONVERTERS.update(converters)
            url_converters.get_converters.cache_clear()
            clear_url_caches()
    # Leaving override_settings rebuilds djoser.conf.settings from the original
    # DJOSER and the restored defaults.


@pytest.fixture
def djoser_startup_settings():
    """
    Run code as if ``DJOSER`` had been set in settings.py when Django started.

    Plain ``override_settings(DJOSER=...)`` only reaches code that reads
    ``djoser.conf.settings`` per request. Values read at import time, such as
    ``permission_classes = settings.PERMISSIONS.user_create`` or the views a URL
    module picks, keep their startup values. This fixture returns a context manager
    that overrides ``DJOSER`` (the dict replaces the project's DJOSER, it is not
    merged), then imports djoser's view and URL modules, the social and webauthn
    ones and ROOT_URLCONF again. On exit, even on failure, the original module
    objects, settings and URL caches are put back, so classes imported before the
    block are the ones serving requests again.

    Usage::

        def test_custom_permission(djoser_startup_settings, authenticated_client):
            admin_only = ["rest_framework.permissions.IsAdminUser"]
            data = {"username": "new", "password": "Secr3t!pass"}
            with djoser_startup_settings({"PERMISSIONS": {"user_create": admin_only}}):
                response = authenticated_client.post("/auth/users/", data)
            assert response.status_code == 403

    Pass ``modules=["myproject.urls_api"]`` to import more modules again, e.g. a URL
    module sitting between ROOT_URLCONF and djoser's, or a module of custom classes
    that read djoser settings at import time. Not imported again: djoser.serializers,
    djoser.permissions and the like, which also capture some settings at import.
    Inside the block, reach view classes through ``sys.modules`` (``mock.patch``
    strings, ``import_module``) rather than names imported at the top of a test
    module, which still point at the original classes. Do not combine with the
    ``djoser_settings`` fixture inside the block.
    """
    return _startup_settings
