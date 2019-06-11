from django.conf.urls import url

from rest_framework_simplejwt import views


urlpatterns = [
    url(r"^jwt/create/?", views.token_obtain_pair, name="jwt-create"),
    url(r"^jwt/refresh/?", views.token_refresh, name="jwt-refresh"),
    url(r"^jwt/verify/?", views.token_verify, name="jwt-verify"),
]
