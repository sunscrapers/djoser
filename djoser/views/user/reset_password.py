from rest_framework import status
from rest_framework.response import Response

from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views.user.base import GenericUserAPIView


class UserResetPasswordAPIView(GenericUserAPIView):
    serializer_class = settings.SERIALIZERS.password_reset
    permission_classes = settings.PERMISSIONS.password_reset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
