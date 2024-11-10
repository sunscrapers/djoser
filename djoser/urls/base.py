from django.contrib.auth import get_user_model
from django.urls import path

from djoser.views.activation import (
    UserActivationAPIView,
    UserResendActivationAPIView,
)
from djoser.views.me import UserMeAPIView
from djoser.views.password import (
    ResetPasswordConfirmViewAPIView,
    ResetPasswordViewAPIView,
    SetPasswordViewAPIView,
)
from djoser.views.user import UserViewSet
from djoser.views.username import (
    ResetUsernameAPIView,
    ResetUsernameConfirmAPIView,
    SetUsernameAPIView,
)

User = get_user_model()

# user
user_list = path(
    "users/", UserViewSet.as_view({"get": "list", "post": "create"}), name="user-list"
)
user_detail = path(
    f"users/<{UserViewSet.lookup_field}>/",
    UserViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    ),
    name="user-detail",
)

# me
me_list = path(
    "users/me/",
    UserMeAPIView.as_view(),
    name="user-me",
)

# activation
user_activation = path(
    "users/activation/", UserActivationAPIView.as_view(), name="user-activation"
)
user_resend_activation = path(
    "users/resend-activation/",
    UserResendActivationAPIView.as_view(),
    name="user-resend-activation",
)

# password
user_password_reset_confirm = path(
    "users/reset_password_confirm/",
    ResetPasswordConfirmViewAPIView.as_view(),
    name="user-reset-password-confirm",
)
user_reset_password = path(
    "users/reset_password",
    ResetPasswordViewAPIView.as_view(),
    name="user-reset-password",
)
user_set_password = path(
    "users/set_password", SetPasswordViewAPIView.as_view(), name="user-set-password"
)

# username
user_reset_username = path(
    f"users/reset_{User.USERNAME_FIELD}",
    ResetUsernameAPIView.as_view(),
    name="user-reset-username",
)
user_reset_username_confirm = path(
    f"users/reset_{User.USERNAME_FIELD}_confirm",
    ResetUsernameConfirmAPIView.as_view(),
    name="user-reset-username-confirm",
)
user_set_username = path(
    f"users/set_{User.USERNAME_FIELD}",
    SetUsernameAPIView.as_view(),
    name="user-set-username",
)

urlpatterns = [
    user_resend_activation,
    user_activation,
    user_password_reset_confirm,
    user_reset_username_confirm,
    user_reset_password,
    user_set_password,
    user_set_username,
    user_reset_username,
    me_list,
    user_detail,
    user_list,
]
