from djoser.conf import settings
from djoser.views.user.user import UserViewSet


class UserMeViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == "destroy":
            serializer_class = super().get_serializer_class()
        else:
            serializer_class = settings.SERIALIZERS.current_user
        return serializer_class

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        queryset = self.queryset.objects.all()
        return queryset.filter(pk=self.request.user.pk)
