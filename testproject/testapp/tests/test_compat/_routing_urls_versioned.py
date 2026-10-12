"""
URLconf mounting djoser under a captured API version, for URLPathVersioning.
"""

from django.urls import include, re_path

urlpatterns = [
    re_path(r"^api/(?P<version>v[0-9]+)/auth/", include("djoser.urls")),
    re_path(r"^api/(?P<version>v[0-9]+)/auth/", include("djoser.urls.authtoken")),
    re_path(r"^api/(?P<version>v[0-9]+)/auth/", include("djoser.urls.jwt")),
]
