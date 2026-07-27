from django.urls import path

from djoser.conf import settings
from djoser.urls.utils import AppendSlashRedirectView

urlpatterns = [
    path("token/login/", settings.VIEWS.token_create.as_view(), name="login"),
    path("token/logout/", settings.VIEWS.token_destroy.as_view(), name="logout"),
    # djoser 2.x accepted these without the trailing slash.
    path("token/login", AppendSlashRedirectView.as_view()),
    path("token/logout", AppendSlashRedirectView.as_view()),
]
