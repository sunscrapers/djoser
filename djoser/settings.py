from copy import deepcopy

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils import six
from django.utils.functional import LazyObject, empty
from django.test.signals import setting_changed


DJOSER_SETTINGS_NAMESPACE = 'DJOSER'


default_settings = {
    'USE_HTML_EMAIL_TEMPLATES': False,
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'SET_PASSWORD_RETYPE': False,
    'SET_USERNAME_RETYPE': False,
    'PASSWORD_RESET_CONFIRM_RETYPE': False,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'ROOT_VIEW_URLS_MAPPING': {},
    'PASSWORD_VALIDATORS': [],
    'SERIALIZERS': {
        'activation': 'djoser.serializers.ActivationSerializer',
        'login': 'djoser.serializers.LoginSerializer',
        'password_reset': 'djoser.serializers.PasswordResetSerializer',
        'password_reset_confirm': 'djoser.serializers.PasswordResetConfirmSerializer',
        'password_reset_confirm_retype': 'djoser.serializers.PasswordResetConfirmRetypeSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'set_password_retype': 'djoser.serializers.SetPasswordRetypeSerializer',
        'set_username': 'djoser.serializers.SetUsernameSerializer',
        'set_username_retype': 'djoser.serializers.SetUsernameRetypeSerializer',
        'user_registration': 'djoser.serializers.UserRegistrationSerializer',
        'user': 'djoser.serializers.UserSerializer',
        'token': 'djoser.serializers.TokenSerializer',
    },
    'LOGOUT_ON_PASSWORD_CHANGE': False,
}


class Settings(object):
    def __init__(self, default_settings, explicit_overriden_settings=None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        for setting_name, setting_value in six.iteritems(default_settings):
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

        overriden_djoser_settings = getattr(settings, DJOSER_SETTINGS_NAMESPACE, {}) or explicit_overriden_settings
        for overriden_setting_name, overriden_setting_value in six.iteritems(overriden_djoser_settings):
            value = overriden_setting_value
            if isinstance(overriden_setting_value, dict):
                value = getattr(self, overriden_setting_name, {})
                value.update(overriden_setting_value)
            setattr(self, overriden_setting_name, value)


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


config = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    global config
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJOSER_SETTINGS_NAMESPACE:
        config._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)

