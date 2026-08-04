from rest_framework import status, generics
from rest_framework.response import Response

from djoser import utils
from djoser.conf import settings
from .base import UserBaseView


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
