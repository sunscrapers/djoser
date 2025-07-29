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
from djoser.views.user import (
    UserListView,
    UserCreateView,
    UserRetrieveView,
    UserUpdateView,
    UserDeleteView,
)
from djoser.views.username import (
    ResetUsernameAPIView,
    ResetUsernameConfirmAPIView,
    SetUsernameAPIView,
)

User = get_user_model()


class CombinedUserListCreateView:
    """
    A simple class that combines list and create operations.

    Dispatches to the appropriate granular view based on HTTP method.
    """

    @staticmethod
    def as_view():
        def view_func(request, *args, **kwargs):
            if request.method == "GET":
                return UserListView.as_view()(request, *args, **kwargs)
            elif request.method == "POST":
                return UserCreateView.as_view()(request, *args, **kwargs)
            else:
                from django.http import HttpResponseNotAllowed

                return HttpResponseNotAllowed(["GET", "POST"])

        # Add attributes for URL introspection
        view_func.http_method_names = ["get", "post"]
        return view_func


class CombinedUserDetailView:
    """
    A simple class that combines retrieve, update, and delete operations.

    Dispatches to the appropriate granular view based on HTTP method.
    """

    @staticmethod
    def as_view():
        def view_func(request, *args, **kwargs):
            if request.method == "GET":
                return UserRetrieveView.as_view()(request, *args, **kwargs)
            elif request.method in ["PUT", "PATCH"]:
                return UserUpdateView.as_view()(request, *args, **kwargs)
            elif request.method == "DELETE":
                return UserDeleteView.as_view()(request, *args, **kwargs)
            else:
                from django.http import HttpResponseNotAllowed

                return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])

        # Add attributes for URL introspection
        view_func.http_method_names = ["get", "put", "patch", "delete"]
        return view_func


# User endpoints - traditional URL names with granular views
user_list_create = path(
    "users/", CombinedUserListCreateView.as_view(), name="user-list"
)

user_detail_update_delete = path(
    f"users/<{UserRetrieveView.lookup_field}>/",
    CombinedUserDetailView.as_view(),
    name="user-detail",
)

# me
me_list = path(
    "users/me/",
    UserMeAPIView.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    ),
    name="user-me",
)

# activation
user_activation = path(
    "users/activation/", UserActivationAPIView.as_view(), name="user-activation"
)
user_resend_activation = path(
    "users/resend_activation/",
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
    "users/reset_password/",
    ResetPasswordViewAPIView.as_view(),
    name="user-reset-password",
)
user_set_password = path(
    "users/set_password/", SetPasswordViewAPIView.as_view(), name="user-set-password"
)

# username
user_reset_username = path(
    f"users/reset_{User.USERNAME_FIELD}/",
    ResetUsernameAPIView.as_view(),
    name="user-reset-username",
)
user_reset_username_confirm = path(
    f"users/reset_{User.USERNAME_FIELD}_confirm/",
    ResetUsernameConfirmAPIView.as_view(),
    name="user-reset-username-confirm",
)
user_set_username = path(
    f"users/set_{User.USERNAME_FIELD}/",
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
    user_detail_update_delete,
    user_list_create,
]
