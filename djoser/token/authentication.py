from rest_framework import authentication
from . import models


class TokenAuthentication(authentication.TokenAuthentication):
    model = models.Token

    @staticmethod
    def get_login_serializer_class():
        from . import serializers
        return serializers.LoginSerializer