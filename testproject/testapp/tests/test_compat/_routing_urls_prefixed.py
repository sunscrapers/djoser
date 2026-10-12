"""
URLconf mounting djoser under a fixed versioned prefix.
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("djoser.urls.authtoken")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
]
