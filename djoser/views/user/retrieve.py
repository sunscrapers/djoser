from rest_framework import generics

from .base import UserBaseView


class UserRetrieveView(UserBaseView, generics.RetrieveAPIView):
    """GET /users/{id}/ - Retrieve user"""

    http_method_names = ["get"]
    action = "retrieve"
