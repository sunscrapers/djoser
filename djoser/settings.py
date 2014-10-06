def get(key):
    from django.conf import settings
    defaults = {
        'DOMAIN': '',
        'SITE_NAME': '',
        'PASSWORD_RESET_CONFIRM_URL': '',
        'ACTIVATION_URL': '',
        'LOGIN_AFTER_REGISTRATION': False,
        'LOGIN_AFTER_ACTIVATION': False,
        'SEND_ACTIVATION_EMAIL': False,
        'SET_PASSWORD_RETYPE': False,
        'SET_USERNAME_RETYPE': False,
        'PASSWORD_RESET_CONFIRM_RETYPE': False,
    }
    defaults.update(getattr(settings, 'DJOSER', {}))
    return defaults[key]