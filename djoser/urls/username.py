from django.contrib.auth import get_user_model
from django.urls import path

from djoser.conf import settings

User = get_user_model()

urlpatterns = []

# Configure username reset endpoint
username_reset_view = getattr(settings.VIEWS, "username_reset", None)
if username_reset_view:
    user_reset_username = path(
        f"users/reset_{User.USERNAME_FIELD}/",
        username_reset_view.as_view(),
        name="user-reset-username",
    )
    urlpatterns.append(user_reset_username)

# Configure username reset confirm endpoint
username_reset_confirm_view = getattr(settings.VIEWS, "username_reset_confirm", None)
if username_reset_confirm_view:
    user_reset_username_confirm = path(
        f"users/reset_{User.USERNAME_FIELD}_confirm/",
        username_reset_confirm_view.as_view(),
        name="user-reset-username-confirm",
    )
    urlpatterns.append(user_reset_username_confirm)

# Configure set username endpoint
set_username_view = getattr(settings.VIEWS, "set_username", None)
if set_username_view:
    user_set_username = path(
        f"users/set_{User.USERNAME_FIELD}/",
        set_username_view.as_view(),
        name="user-set-username",
    )
    urlpatterns.append(user_set_username)
