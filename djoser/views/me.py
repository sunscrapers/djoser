from django.contrib.auth import get_user_model
from rest_framework import status, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class UserMeAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ViewSetMixin,
    GenericUserAPIView,
):
    http_method_names = ["get", "put", "patch", "delete"]
    permission_classes = settings.PERMISSIONS.user
    lookup_field = None

    def get_queryset(self):
        # probably redundant but better safe than sorry
        queryset = self.queryset.objects.all()
        return queryset.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.request.method == "DELETE":
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "DELETE":
            return settings.SERIALIZERS.user_delete
        return settings.SERIALIZERS.current_user

    def get_object(self):
        if settings.HIDE_USERS and not self.request.user.is_authenticated:
            raise NotFound()
        return self.request.user

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def permission_denied(self, request, message=None, code=None):
        if settings.HIDE_USERS and request.user.is_authenticated:
            raise NotFound()
        super().permission_denied(request, message, code)
