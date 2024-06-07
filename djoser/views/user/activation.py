from rest_framework import status
from rest_framework.response import Response

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views.user.base import GenericUserAPIView


class UserActivationAPIView(GenericUserAPIView):
    serializer_class = settings.SERIALIZERS.activation
    permission_classes = settings.PERMISSIONS.activation

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
