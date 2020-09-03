try:
    from django.urls import re_path, include
except ImportError:
    from django.conf.urls import include
    from django.conf.urls import url as re_path


urlpatterns = (
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    re_path(r"^auth/", include("djoser.social.urls")),
)
