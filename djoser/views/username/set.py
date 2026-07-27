from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class SetUsernameAPIView(GenericUserAPIView):
    permission_classes = settings.PERMISSIONS.set_username
    http_method_names = ["post"]

    def get_serializer_class(self):
        if settings.SET_USERNAME_RETYPE:
            return settings.SERIALIZERS.set_username_retype
        return settings.SERIALIZERS.set_username

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        # Use get_user_model() to ensure we get the correct model even if it's mocked
        User = get_user_model()
        new_username = serializer.data["new_" + User.USERNAME_FIELD]

        setattr(user, User.USERNAME_FIELD, new_username)
        user.save()

        if settings.USERNAME_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.username_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)
