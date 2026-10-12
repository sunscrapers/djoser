from rest_framework import generics

from .base import UserBaseView


class UserListView(UserBaseView, generics.ListAPIView):
    """GET /users/ - List users"""

    http_method_names = ["get"]
    action = "list"
    permission_key = "user_list"
