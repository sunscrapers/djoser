from django.utils.module_loading import import_string


def test_settings_should_be_default_if_djoser_not_in_django_settings(djoser_settings):
    djoser_settings.clear()

    from djoser.conf import default_settings
    from djoser.conf import settings as djoser_settings_module

    for setting_name, setting_value in default_settings.items():
        overridden_value = getattr(djoser_settings_module, setting_name)
        try:
            assert setting_value == overridden_value
        except AssertionError:
            setting_value = import_string(setting_value)
            assert setting_value == overridden_value


def test_djoser_simple_setting_overriden(djoser_settings):
    djoser_settings["SET_USERNAME_RETYPE"] = True

    from djoser.conf import settings as djoser_settings_module

    assert djoser_settings_module.SET_USERNAME_RETYPE


def test_djoser_serializer_setting_overriden(djoser_settings):
    djoser_settings["SERIALIZERS"] = {"user": "djoser.serializers.TokenSerializer"}

    from djoser.conf import settings as djoser_settings_module

    assert djoser_settings_module.SERIALIZERS.user.__name__ == "TokenSerializer"
