from django.conf.urls import url, include

from djoser.urls import DjoserRouter


router = DjoserRouter(include_token_urls=True)

urlpatterns = (
    url(r'^', include(router.urls)),
)
