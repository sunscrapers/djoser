from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response

from djoser import signals
from djoser.conf import settings
from djoser.compat import get_user_email

User = get_user_model()


class ActivationView(generics.GenericAPIView):
    permission_classes = settings.PERMISSIONS.activation
    serializer_class = settings.SERIALIZERS.activation

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


class ResendActivationView(generics.GenericAPIView):
    permission_classes = settings.PERMISSIONS.password_reset
    serializer_class = settings.SERIALIZERS.password_reset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
