from django.urls import path

from djoser.views.token.create import TokenCreateView
from djoser.views.token.destroy import TokenDestroyView

urlpatterns = [
    path("token/login/", TokenCreateView.as_view(), name="login"),
    path("token/logout/", TokenDestroyView.as_view(), name="logout"),
]
