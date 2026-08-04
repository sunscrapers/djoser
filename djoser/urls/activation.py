from django.urls import path

from djoser.conf import settings

urlpatterns = []

# Configure activation endpoint
activation_view = getattr(settings.VIEWS, "activation", None)
if activation_view:
    user_activation = path(
        "users/activation/", activation_view.as_view(), name="user-activation"
    )
    urlpatterns.append(user_activation)

# Configure resend activation endpoint
resend_activation_view = getattr(settings.VIEWS, "resend_activation", None)
if resend_activation_view:
    user_resend_activation = path(
        "users/resend_activation/",
        resend_activation_view.as_view(),
        name="user-resend-activation",
    )
    urlpatterns.append(user_resend_activation)
