from django.urls import re_path

from djoser.conf import settings
from djoser.urls.utils import user_url_name

urlpatterns = []

# Configure password reset confirm endpoint
password_reset_confirm_view = getattr(settings.VIEWS, "password_reset_confirm", None)
if password_reset_confirm_view:
    user_password_reset_confirm = re_path(
        r"^users/reset_password_confirm/$",
        password_reset_confirm_view.as_view(),
        name=user_url_name("reset-password-confirm"),
    )
    urlpatterns.append(user_password_reset_confirm)

# Configure password reset endpoint
password_reset_view = getattr(settings.VIEWS, "password_reset", None)
if password_reset_view:
    user_reset_password = re_path(
        r"^users/reset_password/$",
        password_reset_view.as_view(),
        name=user_url_name("reset-password"),
    )
    urlpatterns.append(user_reset_password)

# Configure set password endpoint
set_password_view = getattr(settings.VIEWS, "set_password", None)
if set_password_view:
    user_set_password = re_path(
        r"^users/set_password/$",
        set_password_view.as_view(),
        name=user_url_name("set-password"),
    )
    urlpatterns.append(user_set_password)
