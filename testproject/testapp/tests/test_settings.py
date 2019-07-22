from django.conf import settings
from django.test.testcases import SimpleTestCase
from django.test.utils import override_settings
from django.utils import six
from django.utils.module_loading import import_string


class SettingsTestCase(SimpleTestCase):
    @override_settings(DJOSER=dict())
    def test_settings_should_be_default_if_djoser_not_in_django_settings(self):
        from djoser.conf import settings as djoser_settings
        from djoser.conf import default_settings

        for setting_name, setting_value in six.iteritems(default_settings):
            overridden_value = getattr(djoser_settings, setting_name)
            try:
                self.assertEqual(setting_value, overridden_value)
            except AssertionError:
                setting_value = import_string(setting_value)
                self.assertEqual(setting_value, overridden_value)

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SET_USERNAME_RETYPE": True}))
    def test_djoser_simple_setting_overriden(self):
        from djoser.conf import settings as djoser_settings

        self.assertTrue(djoser_settings.SET_USERNAME_RETYPE)

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{"SERIALIZERS": {"user": "djoser.serializers.TokenSerializer"}},
        )
    )
    def test_djoser_serializer_setting_overriden(self):
        from djoser.conf import settings as djoser_settings

        self.assertEqual(djoser_settings.SERIALIZERS.user.__name__, "TokenSerializer")
