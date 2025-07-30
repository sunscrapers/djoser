from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

from djoser.conf import settings
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
