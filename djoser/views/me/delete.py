from rest_framework import status, mixins
from rest_framework.response import Response

from djoser import utils
from .base import BaseMeAPIView


class UserMeDeleteView(mixins.DestroyModelMixin, BaseMeAPIView):
    """
    Delete current user account.
    """

    http_method_names = ["delete"]
    permission_key = "user_delete"
    serializer_key = "user_delete"

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
