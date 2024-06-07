from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^signup_request/$",
        views.SignupRequestView.as_view(),
        name="webauthn_signup_request",
    ),
    re_path(
        r"^signup/(?P<ukey>.+)/$", views.SignupView.as_view(), name="webauthn_signup"
    ),
    re_path(
        r"^login_request/$",
        views.LoginRequestView.as_view(),
        name="webauthn_login_request",
    ),
    re_path(r"^login/$", views.LoginView.as_view(), name="webauthn_login"),
]
