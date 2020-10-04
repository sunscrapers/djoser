from django.urls import include, re_path

urlpatterns = (
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    re_path(r"^auth/", include("djoser.social.urls")),
)
