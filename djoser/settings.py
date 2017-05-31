from copy import deepcopy

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.module_loading import import_string

from .compat import lru_cache


default_settings = {
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
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
}


@lru_cache()
def get(key, load=False):
    """Return the value of a settings given a `key`.

    You can write the key as "TOKEN_MODEL" or "SERIALIZERS.login", this function
    will split the key by "." and navigate the settings dictionary in depth.

    If `load=True` the returned value of the key will be imported.
    """
    user_settings = merge_settings_dicts(
        deepcopy(default_settings), getattr(settings, 'DJOSER', {}))
    try:
        for level in key.split('.'):
            value = user_settings[level]
            user_settings = value
        value = import_string(value) if load else value
    except KeyError:
        raise ImproperlyConfigured(
            'Missing settings: DJOSER[\'{key}\']'.format(key=key)
        )
    except ImportError:
        raise ImproperlyConfigured(
            'Can not import "{imp}" in  DJOSER[\'{key}\']'.format(
                imp=value, key=key
            )
        )
    else:
        return value


def merge_settings_dicts(a, b, path=None, overwrite_conflicts=True):
    """merges b into a, modify a in place

    Found at http://stackoverflow.com/a/7205107/1472229
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_settings_dicts(a[key], b[key], path + [str(key)], overwrite_conflicts=overwrite_conflicts)
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                if overwrite_conflicts:
                    a[key] = b[key]
                else:
                    conflict_path = '.'.join(path + [str(key)])
                    raise Exception('Conflict at %s' % conflict_path)
        else:
            a[key] = b[key]
    # Don't let this fool you that a is not modified in place
    return a
