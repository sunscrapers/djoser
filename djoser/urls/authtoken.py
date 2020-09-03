try:  # pragma: no cover
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from djoser import views

urlpatterns = [
    re_path(r"^token/login/?$", views.TokenCreateView.as_view(), name="login"),
    re_path(r"^token/logout/?$", views.TokenDestroyView.as_view(), name="logout"),
]
