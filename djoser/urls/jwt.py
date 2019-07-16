from django.conf.urls import url
from rest_framework_simplejwt import views

urlpatterns = [
    url(r"^jwt/create/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    url(r"^jwt/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    url(r"^jwt/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
]
