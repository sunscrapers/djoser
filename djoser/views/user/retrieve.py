from rest_framework import generics

from djoser.conf import settings
from .base import UserBaseView


class UserRetrieveView(UserBaseView, generics.RetrieveAPIView):
    """GET /users/{id}/ - Retrieve user"""

    http_method_names = ["get"]
    action = "retrieve"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.

        This ensures permissions are evaluated at request time, not class definition
        time. If permission_classes is set directly on this class (e.g., by tests), use
        that. Otherwise, use settings.
        """
        # Check if permission_classes was set directly on this class (not inherited)
        if "permission_classes" in self.__class__.__dict__:
            permission_classes = self.permission_classes
        else:
            permission_classes = settings.PERMISSIONS.user
        return [permission() for permission in permission_classes]
