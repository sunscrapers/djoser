from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics
from djoser.conf import settings


User = get_user_model()


class GenericUserAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    lookup_field = settings.USER_ID_FIELD
    token_generator = default_token_generator  # used in serializers
    http_method_names = []

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
