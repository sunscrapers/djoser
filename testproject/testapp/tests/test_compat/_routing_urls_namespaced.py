"""
URLconf including djoser's URL modules under instance namespaces.
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/auth/", include(("djoser.urls", "djoser"), namespace="djoser")),
    path(
        "api/v1/auth/",
        include(("djoser.urls.authtoken", "djoser-token"), namespace="djoser-token"),
    ),
    path(
        "api/v1/auth/",
        include(("djoser.urls.jwt", "djoser-jwt"), namespace="djoser-jwt"),
    ),
]
