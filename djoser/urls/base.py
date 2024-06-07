from django.contrib.auth import get_user_model
from django.urls import path

from djoser.views.user.activation import UserActivationAPIView
from djoser.views.user.me import UserMeViewSet
from djoser.views.user.password_reset_confirm import UserPasswordResetConfirmAPIView
from djoser.views.user.resend_activation import UserResendActivationAPIView
from djoser.views.user.reset_password import UserResetPasswordAPIView
from djoser.views.user.reset_username import UserResetUsernameAPIView
from djoser.views.user.reset_username_confirm import UserResetUsernameConfirmAPIView
from djoser.views.user.set_password import UserSetPasswordAPIView
from djoser.views.user.set_username import UserSetUsernameAPIView
from djoser.views.user.user import UserViewSet


User = get_user_model()


user_activation = path(
    "users/activation/", UserActivationAPIView.as_view(), name="user-activation"
)
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
user_password_reset_confirm = path(
    "users/reset_password_confirm/",
    UserPasswordResetConfirmAPIView.as_view(),
    name="user-reset-password-confirm",
)
user_resend_activation = path(
    "users/resend-activation/",
    UserResendActivationAPIView.as_view(),
    name="user-resend-activation",
)
user_reset_password = path(
    "users/reset_password",
    UserResetPasswordAPIView.as_view(),
    name="user-reset-password",
)
user_reset_username = path(
    f"users/reset_{User.USERNAME_FIELD}",
    UserResetUsernameAPIView.as_view(),
    name="user-reset-username",
)
user_reset_username_confirm = path(
    f"users/reset_{User.USERNAME_FIELD}_confirm",
    UserResetUsernameConfirmAPIView.as_view(),
    name="user-reset-username-confirm",
)
user_set_password = path(
    "users/set_password", UserSetPasswordAPIView.as_view(), name="user-set-password"
)
user_set_username = path(
    f"users/set_{User.USERNAME_FIELD}",
    UserSetUsernameAPIView.as_view(),
    name="user-set-username",
)

me_list = path(
    "users/me/",
    UserMeViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    ),
    name="user-me",
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
