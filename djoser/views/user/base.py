from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics
from djoser.conf import settings


User = get_user_model()


class GenericUserAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    lookup_field = settings.USER_ID_FIELD
    http_method_names = ["post"]
    token_generator = default_token_generator  # used in serializers
