# Import views for backward compatibility
from django.contrib.auth import get_user_model

from .user import (
    UserListView,
    UserCreateView,
    UserRetrieveView,
    UserUpdateView,
    UserDeleteView,
)

from .me import UserMeAPIView
from .activation import UserActivationAPIView, UserResendActivationAPIView
from .password import (
    ResetPasswordConfirmViewAPIView,
    ResetPasswordViewAPIView,
    SetPasswordViewAPIView,
)
from .username import (
    ResetUsernameAPIView,
    ResetUsernameConfirmAPIView,
    SetUsernameAPIView,
)

# Export User model for backward compatibility with tests
User = get_user_model()

__all__ = [
    # User model
    "User",
    # Individual views for v3
    "UserListView",
    "UserCreateView",
    "UserRetrieveView",
    "UserUpdateView",
    "UserDeleteView",
    # Other views
    "UserMeAPIView",
    "UserActivationAPIView",
    "UserResendActivationAPIView",
    "ResetPasswordConfirmViewAPIView",
    "ResetPasswordViewAPIView",
    "SetPasswordViewAPIView",
    "ResetUsernameAPIView",
    "ResetUsernameConfirmAPIView",
    "SetUsernameAPIView",
]
