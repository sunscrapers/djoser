from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls


urlpatterns = (
    url(r"^auth/", include("djoser.urls.base")),
    url(r"^auth/", include("djoser.urls.authtoken")),
    url(r"^auth/", include("djoser.urls.jwt")),
    url(r"^auth/", include("djoser.social.urls")),
    url(r"^docs/", include_docs_urls()),
)
