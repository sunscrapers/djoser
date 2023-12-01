"""Helper and compatibility functions."""
from typing import Optional
from django.contrib.auth.base_user import AbstractBaseUser


def get_user_email(user: AbstractBaseUser) -> Optional[str]:
    """Returns real user email or None."""
    return getattr(user, user.get_email_field_name(), None)
