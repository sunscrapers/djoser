def get(key):
    from django.conf import settings
    defaults = {
        'DOMAIN': '',
        'SITE_NAME': '',
        'PASSWORD_RESET_CONFIRM_URL': '',
        'LOGIN_AFTER_REGISTRATION': False,
        'LOGIN_AFTER_ACTIVATION': False,
    }
    defaults.update(getattr(settings, 'DJOSER', {}))
    return defaults[key]