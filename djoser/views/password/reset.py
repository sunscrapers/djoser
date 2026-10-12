from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class ResetPasswordViewAPIView(GenericUserAPIView):
    http_method_names = ["post"]
    action = "reset_password"
    permission_key = "password_reset"
    serializer_key = "password_reset"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
