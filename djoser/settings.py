from django.core.exceptions import ImproperlyConfigured


def get(key):
    from django.conf import settings
    defaults = {
        'SEND_ACTIVATION_EMAIL': False,
        'SET_PASSWORD_RETYPE': False,
        'SET_USERNAME_RETYPE': False,
        'PASSWORD_RESET_CONFIRM_RETYPE': False,
        'ROOT_VIEW_URLS_MAPPING': {},
    }
    defaults.update(getattr(settings, 'DJOSER', {}))
    try:
        return defaults[key]
    except KeyError:
        raise ImproperlyConfigured('Missing settings: DJOSER[\'{}\']'.format(key))