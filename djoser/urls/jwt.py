from django.urls import re_path
from rest_framework_simplejwt import views

# The trailing slash is optional, as in 2.x: reverse() returns the slash-less URL.
# Unlike 2.x the patterns end with $, so /jwt/createx no longer matches.
urlpatterns = [
    re_path(r"^jwt/create/?$", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^jwt/refresh/?$", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^jwt/verify/?$", views.TokenVerifyView.as_view(), name="jwt-verify"),
]
