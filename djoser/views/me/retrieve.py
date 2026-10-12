from rest_framework import mixins

from .base import BaseMeAPIView


class UserMeRetrieveView(mixins.RetrieveModelMixin, BaseMeAPIView):
    """
    Retrieve current user details.
    """

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
