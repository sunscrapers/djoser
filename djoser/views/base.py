from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics
from rest_framework.views import APIView

from djoser.conf import settings


User = get_user_model()


class GenericUserAPIView(generics.GenericAPIView):
    """
    Base for the views that replace 2.x's UserViewSet.

    Custom permissions and serializers written for 2.x keep working: ``action`` holds
    the name the viewset gave the endpoint, and the DJOSER PERMISSIONS and SERIALIZERS
    keys are read on every request, so ``override_settings`` reaches them.
    """

    queryset = User.objects.all()
    lookup_field = settings.USER_ID_FIELD
    token_generator = default_token_generator  # used in serializers
    http_method_names = []
    # UserViewSet's action name for this endpoint, e.g. "me" or "set_password".
    action = None
    # Keys of DJOSER["PERMISSIONS"] and DJOSER["SERIALIZERS"] this endpoint uses.
    permission_key = None
    serializer_key = None

    def __init_subclass__(cls, **kwargs):
        # Views list their methods explicitly so PUT and PATCH can be separate
        # views. Keep HEAD (served by GET) and OPTIONS, which Django and DRF
        # allow by default and which the 2.x viewset answered.
        super().__init_subclass__(**kwargs)
        names = list(cls.http_method_names)
        if "get" in names and "head" not in names:
            names.append("head")
        if "options" not in names:
            names.append("options")
        cls.http_method_names = names

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # Like the viewset: OPTIONS is the "metadata" action, and a method this
        # endpoint does not implement has no action at all.
        method = request.method.lower()
        if method == "options":
            self.action = "metadata"
        elif method not in self.http_method_names or not hasattr(self, method):
            self.action = None
        return request

    def get_permissions(self):
        if self.permission_classes is not APIView.permission_classes:
            # Set on a subclass, e.g. a view swapped in through VIEWS.
            return super().get_permissions()
        # 2.x checked OPTIONS and methods without a handler against the viewset's
        # default, PERMISSIONS.user.
        if self.action in (None, "metadata"):
            key = "user"
        else:
            key = self.permission_key
        if key is None:
            return super().get_permissions()
        return [permission() for permission in getattr(settings.PERMISSIONS, key)]

    def get_serializer_key(self):
        return self.serializer_key

    def get_serializer_class(self):
        key = self.get_serializer_key()
        if self.serializer_class is not None or key is None:
            return super().get_serializer_class()
        return getattr(settings.SERIALIZERS, key)
