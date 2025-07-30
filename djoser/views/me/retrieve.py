from rest_framework import mixins

from djoser.conf import settings
from .base import BaseMeAPIView


class UserMeRetrieveView(mixins.RetrieveModelMixin, BaseMeAPIView):
    """
    Retrieve current user details.
    """

    http_method_names = ["get"]

    def get_serializer_class(self):
        return settings.SERIALIZERS.current_user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
