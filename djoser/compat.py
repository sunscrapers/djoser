from djoser.conf import settings

__all__ = ['settings']


def get_user_email(user):
    email_field_name = get_user_email_field_name(user)
    return getattr(user, email_field_name, None)


def get_user_email_field_name(user):
    try:  # Assume we are Django >= 1.11
        return user.get_email_field_name()
    except AttributeError:  # we are using Django < 1.11
        return settings.USER_EMAIL_FIELD_NAME
