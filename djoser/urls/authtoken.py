from django.urls import re_path

from djoser.conf import settings

# The trailing slash is optional, as in 2.x: reverse() returns the slash-less URL.
urlpatterns = [
    re_path(r"^token/login/?$", settings.VIEWS.token_create.as_view(), name="login"),
    re_path(r"^token/logout/?$", settings.VIEWS.token_destroy.as_view(), name="logout"),
]
