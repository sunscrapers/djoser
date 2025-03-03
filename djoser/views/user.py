from django.contrib.auth import get_user_model
from rest_framework import status, mixins, generics, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email

from djoser.views.base import GenericUserAPIView

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    ViewSetMixin,
    GenericUserAPIView,
):
    serializer_class = settings.SERIALIZERS.user
    permission_classes = settings.PERMISSIONS.user
    http_method_names = ["get", "post", "path", "put", "delete"]

    def permission_denied(self, request, **kwargs):
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "destroy":
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                serializer_class = settings.SERIALIZERS.user_create_password_retype
            else:
                serializer_class = settings.SERIALIZERS.user_create
        elif self.action == "destroy":
            serializer_class = settings.SERIALIZERS.user_delete
        else:
            serializer_class = self.serializer_class
        return serializer_class

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer, *args, **kwargs)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # should we send activation email after update?
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


class UserBaseView(GenericUserAPIView):
    """Base view for user views with common methods."""
    serializer_class = settings.SERIALIZERS.user

    def permission_denied(self, request, **kwargs):
        action = getattr(self, 'action', None)
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        action = getattr(self, 'action', None)
        if settings.HIDE_USERS and action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset


class UserListView(UserBaseView, generics.ListAPIView):
    """View for listing users."""
    permission_classes = settings.PERMISSIONS.user_list
    http_method_names = ["get"]


class UserCreateView(UserBaseView, generics.CreateAPIView):
    """View for creating a user."""
    permission_classes = settings.PERMISSIONS.user_create
    http_method_names = ["post"]
    
    def get_serializer_class(self):
        if settings.USER_CREATE_PASSWORD_RETYPE:
            return settings.SERIALIZERS.user_create_password_retype
        return settings.SERIALIZERS.user_create
    
    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)


class UserListCreateView(UserBaseView, generics.ListCreateAPIView):
    """View for listing and creating users."""
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = settings.PERMISSIONS.user_create
        else:
            self.permission_classes = settings.PERMISSIONS.user_list
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        return self.serializer_class
    
    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {"user": user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)


class UserRetrieveView(UserBaseView, generics.RetrieveAPIView):
    """View for retrieving a user."""
    permission_classes = settings.PERMISSIONS.user
    http_method_names = ["get"]


class UserUpdateView(UserBaseView, generics.UpdateAPIView):
    """View for updating a user."""
    permission_classes = settings.PERMISSIONS.user
    http_method_names = ["put", "patch"]
    
    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer, *args, **kwargs)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # should we send activation email after update?
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)


class UserDeleteView(UserBaseView, generics.DestroyAPIView):
    """View for deleting a user."""
    permission_classes = settings.PERMISSIONS.user_delete
    http_method_names = ["delete"]
    
    def get_serializer_class(self):
        return settings.SERIALIZERS.user_delete
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
