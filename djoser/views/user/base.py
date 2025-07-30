from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

from djoser.conf import settings
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
