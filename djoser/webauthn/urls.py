from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r"^signup_request/$",
        views.SingupRequestView.as_view(),
        name="webauthn_signup_request",
    ),
    url(r"^signup/(?P<ukey>.+)/$", views.SignupView.as_view(), name="webauthn_signup"),
    url(
        r"^login_request/$",
        views.LoginRequestView.as_view(),
        name="webauthn_login_request",
    ),
    url(r"^login/$", views.LoginView.as_view(), name="webauthn_login"),
]
