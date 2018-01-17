import warnings

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed
from django.utils import six
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


DJOSER_SETTINGS_NAMESPACE = 'DJOSER'


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            is_list_of_strings = (
                isinstance(self[item], list) and
                all(isinstance(elem, str) for elem in self[item])
            )

            if is_list_of_strings:
                self[item] = [import_string(func) for func in self[item]]
            elif isinstance(self[item], str):
                self[item] = import_string(self[item])
            value = self[item]
        except KeyError:
            value = super(ObjDict, self).__getattribute__(item)

        return value


default_settings = {
    'PASSWORD_UPDATE_REQUIRE_RETYPE': False,
    'USERNAME_UPDATE_REQUIRE_RETYPE': False,
    'PASSWORD_RESET_CONFIRM_REQUIRE_RETYPE': False,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'PASSWORD_VALIDATORS': [],
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'SOCIAL_AUTH_TOKEN_STRATEGY': 'djoser.social.token.jwt.TokenStrategy',
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': [],
    'TOKEN_MODEL': None,

    'PIPELINES': ObjDict({
        'user_activate': [
            'djoser.pipelines.user_activate.serialize_request',
            'djoser.pipelines.user_activate.perform',
            'djoser.pipelines.user_activate.signal',
            'djoser.pipelines.email.confirmation_email',
        ],
        'user_create': [
            'djoser.pipelines.user_create.serialize_request',
            'djoser.pipelines.user_create.perform',
            'djoser.pipelines.user_create.serialize_instance',
            'djoser.pipelines.user_create.signal',
            'djoser.pipelines.email.activation_email',
        ],
        'user_update': [
            'djoser.pipelines.user_update.serialize_request',
            'djoser.pipelines.user_update.perform',
            'djoser.pipelines.user_update.signal',
            'djoser.pipelines.user_update.serialize_instance',
        ],
        'user_delete': [
            'djoser.pipelines.user_delete.serialize_request',
            'djoser.pipelines.user_delete.perform',
            'djoser.pipelines.user_delete.signal',
        ],
        'user_detail': [
            'djoser.pipelines.user_detail.perform',
            'djoser.pipelines.user_detail.serialize_instance',
        ],
        'username_update': [
            'djoser.pipelines.username_update.serialize_request',
            'djoser.pipelines.username_update.perform',
            'djoser.pipelines.username_update.signal',
        ],
        'password_update': [
            'djoser.pipelines.password_update.serialize_request',
            'djoser.pipelines.password_update.perform',
            'djoser.pipelines.password_update.signal',
        ],
        'password_reset': [
            'djoser.pipelines.password_reset.serialize_request',
            'djoser.pipelines.password_reset.perform',
        ],
        'password_reset_confirm': [
            'djoser.pipelines.password_reset_confirm.serialize_request',
            'djoser.pipelines.password_reset_confirm.perform',
            'djoser.pipelines.password_reset_confirm.signal',
        ],
        'token_create': [
            'djoser.pipelines.token_create.serialize_request',
            'djoser.pipelines.token_create.perform',
            'djoser.pipelines.token_create.signal',
        ],
        'token_destroy': [
            'djoser.pipelines.token_destroy.perform',
            'djoser.pipelines.token_destroy.signal',
        ]
    }),
    'SERIALIZERS': ObjDict({
        'user_activate':
            'djoser.serializers.UserActivateSerializer',
        'password_reset':
            'djoser.serializers.PasswordResetSerializer',
        'password_reset_confirm':
            'djoser.serializers.PasswordResetConfirmSerializer',
        'password_reset_confirm_retype':
            'djoser.serializers.PasswordResetConfirmRetypeSerializer',
        'set_password':
            'djoser.serializers.SetPasswordSerializer',
        'set_password_retype':
            'djoser.serializers.SetPasswordRetypeSerializer',
        'set_username':
            'djoser.serializers.SetUsernameSerializer',
        'set_username_retype':
            'djoser.serializers.SetUsernameRetypeSerializer',
        'user_create':
            'djoser.serializers.UserCreateSerializer',
        'user_delete':
            'djoser.serializers.UserDeleteSerializer',
        'user':
            'djoser.serializers.UserSerializer',
        'token':
            'djoser.serializers.TokenSerializer',
        'token_create':
            'djoser.serializers.TokenCreateSerializer',
    }),
    'EMAIL': ObjDict({
        'activation': 'djoser.email.ActivationEmail',
        'confirmation': 'djoser.email.ConfirmationEmail',
        'password_reset': 'djoser.email.PasswordResetEmail',
    }),
}

SETTINGS_TO_IMPORT = ['TOKEN_MODEL', 'SOCIAL_AUTH_TOKEN_STRATEGY']


class Settings(object):
    def __init__(self, default_settings, explicit_overriden_settings=None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = getattr(
            django_settings, DJOSER_SETTINGS_NAMESPACE, {}
        ) or explicit_overriden_settings

        self._load_default_settings()
        self._override_settings(overriden_settings)
        self._init_settings_to_import()

    def _load_default_settings(self):
        for setting_name, setting_value in six.iteritems(default_settings):
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings):
        for setting_name, setting_value in six.iteritems(overriden_settings):
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
                value.update(ObjDict(setting_value))
            setattr(self, setting_name, value)

    def _init_settings_to_import(self):
        for setting_name in SETTINGS_TO_IMPORT:
            value = getattr(self, setting_name)
            if isinstance(value, str):
                setattr(self, setting_name, import_string(value))


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    global settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)
