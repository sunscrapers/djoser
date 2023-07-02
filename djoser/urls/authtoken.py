from django.urls import path

from djoser import views

urlpatterns = [
    path("token/login/", views.TokenCreateView.as_view(), name="login"),
    path("token/logout/", views.TokenDestroyView.as_view(), name="logout"),
]
