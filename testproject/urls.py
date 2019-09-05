from django.conf.urls import include, url
from django.urls import path

urlpatterns = (
    url(r"^auth/", include("djoser.urls.base")),
    url(r"^auth/", include("djoser.urls.authtoken")),
    url(r"^auth/", include("djoser.urls.jwt")),
    url(r"^auth/", include("djoser.social.urls")),
    path("webauthn/", include("djoser.webauthn.urls")),
)
