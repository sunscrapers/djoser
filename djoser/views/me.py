from django.contrib.auth import get_user_model
from rest_framework import status, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class BaseMeAPIView(GenericUserAPIView):
    """
    Base class for user 'me' views with common functionality.
    """

    permission_classes = settings.PERMISSIONS.user
    lookup_field = None

    def get_queryset(self):
        queryset = self.queryset.objects.all()
        return queryset.filter(pk=self.request.user.pk)

    def get_object(self):
        if settings.HIDE_USERS and not self.request.user.is_authenticated:
            raise NotFound()
        return self.request.user

    def permission_denied(self, request, message=None, code=None):
        if settings.HIDE_USERS and request.user.is_authenticated:
            raise NotFound()
        super().permission_denied(request, message, code)


class UserMeRetrieveView(mixins.RetrieveModelMixin, BaseMeAPIView):
    """
    Retrieve current user details.
    """

    http_method_names = ["get"]

    def get_serializer_class(self):
        return settings.SERIALIZERS.current_user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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


class UserMeDeleteView(mixins.DestroyModelMixin, BaseMeAPIView):
    """
    Delete current user account.
    """

    http_method_names = ["delete"]

    def get_permissions(self):
        self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        return settings.SERIALIZERS.user_delete

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
