from rest_framework import mixins

from djoser import signals
from djoser.conf import settings
from djoser.compat import get_user_email
from .base import BaseMeAPIView


class UserMeUpdateView(mixins.UpdateModelMixin, BaseMeAPIView):
    """
    Update current user details.
    """

    http_method_names = ["put", "patch"]

    def get_serializer_class(self):
        return settings.SERIALIZERS.current_user

    def perform_update(self, serializer):
        super().perform_update(serializer)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
