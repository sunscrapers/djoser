from django.contrib.auth import get_user_model, update_session_auth_hash
from rest_framework import status
from rest_framework.response import Response

from djoser import utils
from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class SetPasswordViewAPIView(GenericUserAPIView):
    permission_classes = settings.PERMISSIONS.set_password
    http_method_names = ["post"]

    def get_serializer_class(self):
        if settings.SET_PASSWORD_RETYPE:
            return settings.SERIALIZERS.set_password_retype
        return settings.SERIALIZERS.set_password

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
