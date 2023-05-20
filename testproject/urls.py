from django.urls import include, re_path
from django.views.generic import TemplateView

urlpatterns = (
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    re_path(r"^auth/", include("djoser.social.urls")),
    re_path(r"^webauthn/", include("djoser.webauthn.urls")),
    re_path(
        r"^webauthn-example/$", TemplateView.as_view(template_name="webauthn.html")
    ),
)
