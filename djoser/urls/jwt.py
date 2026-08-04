from django.urls import path
from rest_framework_simplejwt import views

from djoser.urls.utils import AppendSlashRedirectView

urlpatterns = [
    path("jwt/create/", views.TokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", views.TokenVerifyView.as_view(), name="jwt-verify"),
    # djoser 2.x accepted these without the trailing slash.
    path("jwt/create", AppendSlashRedirectView.as_view()),
    path("jwt/refresh", AppendSlashRedirectView.as_view()),
    path("jwt/verify", AppendSlashRedirectView.as_view()),
]
