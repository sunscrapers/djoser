from django.urls import re_path

from djoser.conf import settings
from djoser.urls.utils import user_url_name

urlpatterns = []

# Configure activation endpoint
activation_view = getattr(settings.VIEWS, "activation", None)
if activation_view:
    user_activation = re_path(
        r"^users/activation/$",
        activation_view.as_view(),
        name=user_url_name("activation"),
    )
    urlpatterns.append(user_activation)

# Configure resend activation endpoint
resend_activation_view = getattr(settings.VIEWS, "resend_activation", None)
if resend_activation_view:
    user_resend_activation = re_path(
        r"^users/resend_activation/$",
        resend_activation_view.as_view(),
        name=user_url_name("resend-activation"),
    )
    urlpatterns.append(user_resend_activation)
