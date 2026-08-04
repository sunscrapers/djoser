from rest_framework import generics

from djoser.conf import settings
from .base import UserBaseView


class UserListView(UserBaseView, generics.ListAPIView):
    """GET /users/ - List users"""

    permission_classes = settings.PERMISSIONS.user_list
    http_method_names = ["get"]
    action = "list"
