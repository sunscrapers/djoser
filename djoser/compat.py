from djoser.conf import settings

try:
    from django.contrib.auth.password_validation import validate_password
except ImportError:
    from password_validation import validate_password

try:
    from django.core.urlresolvers import NoReverseMatch
except ImportError:
    from django.urls.exceptions import NoReverseMatch

__all__ = ['settings', 'validate_password', 'NoReverseMatch']


def get_user_email(user):
    email_field_name = get_user_email_field_name(user)
    return getattr(user, email_field_name, None)


def get_user_email_field_name(user):
    try:  # Assume we are Django >= 1.11
        return user.get_email_field_name()
    except AttributeError:  # we are using Django < 1.11
        return settings.USER_EMAIL_FIELD_NAME
