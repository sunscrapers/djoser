from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from djoser import constants

User = get_user_model()


def encode_uid(pk):
    return urlsafe_base64_encode(force_bytes(pk)).decode()


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


def get_user_email(user):
    user_has_email_field = hasattr(User, 'get_email_field_name')
    assert user_has_email_field, constants.ASSERT_USER_EMAIL_FIELD_EXISTS
    return getattr(user, user.get_email_field_name(), None)


def get_users_for_email(email):
    email_field_name = User.get_email_field_name()
    users = User._default_manager.filter(**{
        email_field_name + '__iexact': email
    })
    return [u for u in users if u.is_active]
