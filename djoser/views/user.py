from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class UserBaseView(GenericUserAPIView):
    """
    Base view for user views with common methods.
    """

    serializer_class = settings.SERIALIZERS.user

    def permission_denied(self, request, message=None, code=None):
        action = getattr(self, "action", None)
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and action in ["update", "partial_update", "list", "retrieve"]
        ):
            # For HIDE_USERS=True, we generally want to return 404 to hide user
            # existence. Exception:
            # 1. CurrentUserOrAdmin should show 403 because it's the default
            # 2. For READ operations (retrieve), CurrentUserOrAdminOrReadOnly
            #    should work normally because it explicitly allows read access
            from djoser.permissions import (
                CurrentUserOrAdmin,
                CurrentUserOrAdminOrReadOnly,
            )

            # Get permission classes from either the attribute or get_permissions()
            permission_classes = getattr(self, "permission_classes", None)
            if permission_classes is None:
                # If permission_classes is not set, get them from get_permissions()
                permissions = self.get_permissions()
                permission_classes = [perm.__class__ for perm in permissions]

            has_default_permission = any(
                perm_class == CurrentUserOrAdmin for perm_class in permission_classes
            )

            has_read_only_permission = any(
                perm_class == CurrentUserOrAdminOrReadOnly
                for perm_class in permission_classes
            )

            # Don't raise 404 if:
            # 1. Using default permission (CurrentUserOrAdmin)
            # 2. Using CurrentUserOrAdminOrReadOnly for read operations
            should_return_403 = has_default_permission or (
                has_read_only_permission and action == "retrieve"
            )

            if not should_return_403:
                # Non-default permissions for write operations should return 404
                # to hide user existence
                raise NotFound()
        super().permission_denied(request, message, code)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        action = getattr(self, "action", None)
        if settings.HIDE_USERS and action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset


class UserListView(UserBaseView, generics.ListAPIView):
    """GET /users/ - List users"""

    permission_classes = settings.PERMISSIONS.user_list
    http_method_names = ["get"]
    action = "list"


class UserCreateView(UserBaseView, generics.CreateAPIView):
    """POST /users/ - Create user"""

    permission_classes = settings.PERMISSIONS.user_create
    http_method_names = ["post"]
    action = "create"

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


class UserRetrieveView(UserBaseView, generics.RetrieveAPIView):
    """GET /users/{id}/ - Retrieve user"""

    http_method_names = ["get"]
    action = "retrieve"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.

        This ensures permissions are evaluated at request time, not class definition
        time. If permission_classes is set directly on this class (e.g., by tests), use
        that. Otherwise, use settings.
        """
        # Check if permission_classes was set directly on this class (not inherited)
        if "permission_classes" in self.__class__.__dict__:
            permission_classes = self.permission_classes
        else:
            permission_classes = settings.PERMISSIONS.user
        return [permission() for permission in permission_classes]


class UserPutView(UserBaseView, generics.UpdateAPIView):
    """PUT /users/{id}/ - Full update user"""

    http_method_names = ["put"]
    action = "update"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Check if permission_classes was set directly on this class (not inherited)
        if "permission_classes" in self.__class__.__dict__:
            permission_classes = self.permission_classes
        else:
            permission_classes = settings.PERMISSIONS.user
        return [permission() for permission in permission_classes]

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


class UserPatchView(UserBaseView, generics.UpdateAPIView):
    """PATCH /users/{id}/ - Partial update user"""

    http_method_names = ["patch"]
    action = "partial_update"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Check if permission_classes was set directly on this class (not inherited)
        if "permission_classes" in self.__class__.__dict__:
            permission_classes = self.permission_classes
        else:
            permission_classes = settings.PERMISSIONS.user
        return [permission() for permission in permission_classes]

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
    """DELETE /users/{id}/ - Delete user"""

    http_method_names = ["delete"]
    action = "destroy"

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.

        This ensures permissions are evaluated at request time, not class definition
        time.
        """
        permission_classes = settings.PERMISSIONS.user_delete
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return settings.SERIALIZERS.user_delete

    def destroy(self, request, *args, **kwargs):
        # Ensure permissions are checked first
        self.check_permissions(request)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
