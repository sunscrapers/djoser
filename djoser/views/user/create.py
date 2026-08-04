from rest_framework import generics

from djoser import signals
from djoser.conf import settings
from djoser.compat import get_user_email
from .base import UserBaseView


class UserCreateView(UserBaseView, generics.CreateAPIView):
    """POST /users/ - Create user"""

    permission_classes = settings.PERMISSIONS.user_create
    http_method_names = ["post"]
    action = "create"

    def get_serializer_class(self):
        if settings.USER_CREATE_PASSWORD_RETYPE:
            return settings.SERIALIZERS.user_create_password_retype
        return settings.SERIALIZERS.user_create

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)
