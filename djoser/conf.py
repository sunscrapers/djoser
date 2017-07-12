import warnings

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed
from django.utils import six
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


DJOSER_SETTINGS_NAMESPACE = 'DJOSER'


default_settings = {
    'USE_HTML_EMAIL_TEMPLATES': False,
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'SEND_REREGISTRATION_EMAIL': False,
    'SET_PASSWORD_RETYPE': False,
    'SET_USERNAME_RETYPE': False,
    'PASSWORD_RESET_CONFIRM_RETYPE': False,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'ROOT_VIEW_URLS_MAPPING': {},
    'PASSWORD_VALIDATORS': [],
    'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
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
    'USER_EMAIL_FIELD_NAME': 'email',
    'REREGISTRATION_SHOW_RESPONSE': True,
}

SETTINGS_TO_IMPORT = ['TOKEN_MODEL']


class Settings(object):
    def __init__(self, default_settings, explicit_overriden_settings=None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        for setting_name, setting_value in six.iteritems(default_settings):
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

        overriden_djoser_settings = getattr(
            django_settings, DJOSER_SETTINGS_NAMESPACE, {}
        ) or explicit_overriden_settings

        for overriden_setting_name, overriden_setting_value in six.iteritems(
                overriden_djoser_settings
        ):
            value = overriden_setting_value
            if isinstance(overriden_setting_value, dict):
                value = getattr(self, overriden_setting_name, {})
                value.update(overriden_setting_value)
            setattr(self, overriden_setting_name, value)

        self._init_settings_to_import()

    def _init_settings_to_import(self):
        for setting_name in SETTINGS_TO_IMPORT:
            value = getattr(self, setting_name)
            setattr(self, setting_name, import_string(value))


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)

    def get(self, key):
        """
        This function is here only to provide backwards compatibility in
        case anyone uses old settings interface.
        It is strongly encouraged to use dot notation.
        """
        warnings.warn(
            'The settings.get(key) is superseded by the dot attribute access.',
            PendingDeprecationWarning
        )
        try:
            return getattr(self, key)
        except AttributeError:
            raise ImproperlyConfigured('Missing settings: {}[\'{}\']'.format(
                DJOSER_SETTINGS_NAMESPACE, key)
            )


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    global settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)

