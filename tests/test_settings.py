from django.utils import six
from django.utils.module_loading import import_string


def test_settings_should_be_default_if_not_defined(settings):
    settings.DJOSER = dict()

    from djoser.conf import settings as djoser_settings
    from djoser.conf import default_settings

    for setting_name, setting_value in six.iteritems(default_settings):
        overridden_value = getattr(djoser_settings, setting_name)
        try:
            assert setting_value == overridden_value
        except AssertionError:
            setting_value = import_string(setting_value)
            assert setting_value == overridden_value


def test_djoser_simple_setting_overriden(settings):
    settings.DJOSER = dict(
        settings.DJOSER, **{'USERNAME_UPDATE_REQUIRE_RETYPE': True}
    )

    from djoser.conf import settings as djoser_settings
    assert djoser_settings.USERNAME_UPDATE_REQUIRE_RETYPE


def test_djoser_serializer_setting_overriden(settings):
    settings.DJOSER = dict(settings.DJOSER, **{
        'SERIALIZERS': {'fake': 'djoser.serializers.TokenSerializer'}
    })

    from djoser.conf import settings as djoser_settings
    assert djoser_settings.SERIALIZERS['fake'].__name__ == 'TokenSerializer'
