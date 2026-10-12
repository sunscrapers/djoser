from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

from djoser.conf import settings
from djoser.views.base import GenericUserAPIView

User = get_user_model()


class UserBaseView(GenericUserAPIView):
    """
    Base view for user views with common methods.
    """

    permission_key = "user"
    serializer_key = "user"

    def permission_denied(self, request, message=None, code=None):
        if (
            settings.HIDE_USERS
            and request.user.is_authenticated
            and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, message, code)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset
