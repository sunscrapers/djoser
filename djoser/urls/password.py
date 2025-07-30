from django.urls import path

from djoser.conf import settings

urlpatterns = []

# Configure password reset confirm endpoint
password_reset_confirm_view = getattr(settings.VIEWS, "password_reset_confirm", None)
if password_reset_confirm_view:
    user_password_reset_confirm = path(
        "users/reset_password_confirm/",
        password_reset_confirm_view.as_view(),
        name="user-reset-password-confirm",
    )
    urlpatterns.append(user_password_reset_confirm)

# Configure password reset endpoint
password_reset_view = getattr(settings.VIEWS, "password_reset", None)
if password_reset_view:
    user_reset_password = path(
        "users/reset_password/",
        password_reset_view.as_view(),
        name="user-reset-password",
    )
    urlpatterns.append(user_reset_password)

# Configure set password endpoint
set_password_view = getattr(settings.VIEWS, "set_password", None)
if set_password_view:
    user_set_password = path(
        "users/set_password/", set_password_view.as_view(), name="user-set-password"
    )
    urlpatterns.append(user_set_password)
