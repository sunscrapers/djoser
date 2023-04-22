from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^request/email/$",
        views.ObtainEmailCallbackToken.as_view(),
        name="passwordless_email_signup_request",
    ),
    re_path(
        r"^request/mobile/$",
        views.ObtainMobileCallbackToken.as_view(),
        name="passwordless_mobile_signup_request",
    ),
    re_path(
        r"^exchange/$",
        views.ExchangePasswordlessTokenForAuthTokenView.as_view(),
        name="passwordless_token_exchange",
    )
]
