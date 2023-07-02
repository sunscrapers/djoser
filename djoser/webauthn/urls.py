from django.urls import path

from . import views

urlpatterns = [
    path(
        "signup_request/",
        views.SingupRequestView.as_view(),
        name="webauthn_signup_request",
    ),
    path("signup/<ukey>/", views.SignupView.as_view(), name="webauthn_signup"),
    path(
        "login_request/",
        views.LoginRequestView.as_view(),
        name="webauthn_login_request",
    ),
    path("login/", views.LoginView.as_view(), name="webauthn_login"),
]
