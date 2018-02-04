from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils import six
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


DJOSER_SETTINGS_NAMESPACE = 'DJOSER'

default_settings = {
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'PASSWORD_VALIDATORS': [],
    'TOKEN_MODEL': None,
    'VIEW_PIPELINE_ADAPTER':
        'djoser.pipelines.base.default_view_pipeline_adapter',

    'PIPELINES': {
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
            'djoser.pipelines.email.confirmation_email',
        ],
        'user_detail': [
            'djoser.pipelines.user_detail.perform',
            'djoser.pipelines.user_detail.serialize_instance',
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
            'djoser.pipelines.token_create.serialize_instance',
        ],
        'token_delete': [
            'djoser.pipelines.token_delete.perform',
            'djoser.pipelines.token_delete.signal',
        ]
    },
    'SERIALIZERS': {
        'user_activate':
            'djoser.serializers.UserActivateSerializer',
        'user_create':
            'djoser.serializers.UserCreateSerializer',
        'user':
            'djoser.serializers.UserSerializer',
        'user_delete':
            'djoser.serializers.UserDeleteSerializer',
        'username_update':
            'djoser.serializers.UsernameUpdateSerializer',
        'password_update':
            'djoser.serializers.PasswordUpdateSerializer',
        'password_reset':
            'djoser.serializers.PasswordResetSerializer',
        'password_reset_confirm':
            'djoser.serializers.PasswordResetConfirmSerializer',
        'token':
            'djoser.serializers.TokenSerializer',
        'token_create':
            'djoser.serializers.TokenCreateSerializer',
    },
    'EMAIL': {
        'activation': 'djoser.email.ActivationEmail',
        'confirmation': 'djoser.email.ConfirmationEmail',
        'password_reset': 'djoser.email.PasswordResetEmail',
    },
}

SETTINGS_TO_IMPORT = [
    'TOKEN_MODEL', 'VIEW_PIPELINE_ADAPTER', 'PIPELINES', 'SERIALIZERS',
    'EMAIL'
]


class Settings(object):
    def __init__(self, default_settings, explicit_overriden_settings=None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = getattr(
            django_settings, DJOSER_SETTINGS_NAMESPACE, {}
        ) or explicit_overriden_settings

        self._load_default_settings()
        self._override_settings(overriden_settings)

    def __getattribute__(self, item):
        """
        Override is necessary to achieve lazy imports in cases where imported
        resource depends on settings e.g. some serializers use TOKEN_MODEL.
        """
        setting_value = super(Settings, self).__getattribute__(item)
        if item in SETTINGS_TO_IMPORT:
            if isinstance(setting_value, str):
                setting_value = self._import_str_setting(item, setting_value)
            elif isinstance(setting_value, dict):
                setting_value = self._import_dict_setting(item, setting_value)

        return setting_value

    def _import_str_setting(self, item, value):
        value = import_string(value)
        setattr(self, item, value)
        return value

    def _import_dict_setting(self, item, value):
        for dict_key, dict_value in value.items():
            if isinstance(dict_value, str):
                value[dict_key] = import_string(dict_value)
                setattr(self, item, value)

            is_list_of_strings = (
                    isinstance(dict_value, list) and
                    all(isinstance(elem, str) for elem in dict_value)
            )
            if is_list_of_strings:
                value[dict_key] = [
                    import_string(func) for func in dict_value
                ]
                setattr(self, item, value)

        return value

    def _load_default_settings(self):
        for setting_name, setting_value in six.iteritems(default_settings):
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings):
        for setting_name, setting_value in six.iteritems(overriden_settings):
            value = setting_value
            setattr(self, setting_name, value)


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)
