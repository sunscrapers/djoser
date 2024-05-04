from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response

from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views.user.base import GenericUserAPIView


User = get_user_model()


class UserResetUsernameConfirmAPIView(GenericUserAPIView):
    serializer_class = settings.SERIALIZERS.username_reset_confirm
    permission_classes = settings.PERMISSIONS.username_reset_confirm

    def get_serializer_class(self):
        if settings.USERNAME_RESET_CONFIRM_RETYPE:
            return settings.SERIALIZERS.username_reset_confirm_retype
        return settings.SERIALIZERS.username_reset_confirm

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_username = serializer.data["new_" + User.USERNAME_FIELD]

        setattr(serializer.user, User.USERNAME_FIELD, new_username)
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.USERNAME_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.username_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)
