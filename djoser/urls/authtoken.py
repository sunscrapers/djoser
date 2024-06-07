from django.urls import re_path

from djoser.views.token.create import TokenCreateView
from djoser.views.token.destroy import TokenDestroyView

urlpatterns = [
    re_path(r"^token/login/?$", TokenCreateView.as_view(), name="login"),
    re_path(r"^token/logout/?$", TokenDestroyView.as_view(), name="logout"),
]
