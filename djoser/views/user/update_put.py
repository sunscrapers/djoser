from rest_framework import generics

from djoser import signals
from djoser.conf import settings
from djoser.compat import get_user_email
from .base import UserBaseView


class UserPutView(UserBaseView, generics.UpdateAPIView):
    """PUT /users/{id}/ - Full update user"""

    http_method_names = ["put"]
    action = "update"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Check if permission_classes was set directly on this class (not inherited)
        if "permission_classes" in self.__class__.__dict__:
            permission_classes = self.permission_classes
        else:
            permission_classes = settings.PERMISSIONS.user
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer, *args, **kwargs)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # should we send activation email after update?
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)
