# Remove SimpleTestCase import
# from django.test.testcases import SimpleTestCase
# Remove override_settings import as it's not used directly on functions
# from django.test.utils import override_settings
from django.utils.module_loading import import_string

# Import djoser settings modules needed inside functions
from djoser.conf import default_settings
from djoser.conf import settings as djoser_settings


# Use settings fixture instead of decorator
def test_settings_should_be_default_if_djoser_not_in_django_settings(settings):
    # Configure settings *before* reloading djoser settings
    settings.DJOSER = {}

    # Manually reload djoser settings to pick up changes
    djoser_settings._setup()

    for setting_name, setting_value in default_settings.items():
        if setting_name.isupper():  # Check only actual settings
            overridden_value = getattr(djoser_settings, setting_name)
            try:
                assert setting_value == overridden_value
            except AssertionError:
                # Handle potential import string comparison
                try:
                    assert import_string(setting_value) == overridden_value
                except ImportError:
                    # If it's not an import string, direct comparison should work
                    assert setting_value == overridden_value
            except ImportError:
                # Handle cases where default is an import string but cannot be imported
                assert setting_value == overridden_value


# Use settings fixture instead of decorator
def test_djoser_simple_setting_overridden(settings):
    # Configure settings *before* reloading djoser settings
    settings.DJOSER["SET_USERNAME_RETYPE"] = True

    # Manually reload djoser settings to pick up changes
    djoser_settings._setup()

    assert djoser_settings.SET_USERNAME_RETYPE is True


# Use settings fixture instead of decorator
def test_djoser_serializer_setting_overridden(settings):
    # Configure settings *before* reloading djoser settings
    settings.DJOSER["SERIALIZERS"] = {"user": "djoser.serializers.TokenSerializer"}

    # Manually reload djoser settings to pick up changes
    djoser_settings._setup()

    # Accessing SERIALIZERS might auto-import, check the imported class name
    assert djoser_settings.SERIALIZERS.user.__name__ == "TokenSerializer"
