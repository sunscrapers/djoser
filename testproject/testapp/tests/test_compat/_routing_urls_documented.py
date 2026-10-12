"""
URLconf mounting djoser the way its docs show, with path() instead of re_path().
"""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.urls.jwt")),
]
