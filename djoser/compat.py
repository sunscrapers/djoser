try:
    from django.contrib.auth.password_validation import validate_password
except ImportError:
    from password_validation import validate_password

from djoser.conf import settings


def get_user_email(user):
    try:  # Assume we are Django > 1.11
        email_field_name = user.get_email_field_name()
    except AttributeError:  # we are using Django < 1.11
        email_field_name = settings.USER_EMAIL_FIELD_NAME

    return getattr(user, email_field_name, None)

