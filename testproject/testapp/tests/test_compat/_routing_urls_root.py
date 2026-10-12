"""
URLconf mounting djoser at the root, next to views of the project itself.
"""

from django.http import HttpResponse
from django.urls import include, path


def project_view(request):
    return HttpResponse("project")


urlpatterns = [
    path("health/", project_view, name="health"),
    path("", include("djoser.urls")),
    path("", include("djoser.urls.authtoken")),
    path("", include("djoser.urls.jwt")),
    path("pages/about/", project_view, name="about"),
]
