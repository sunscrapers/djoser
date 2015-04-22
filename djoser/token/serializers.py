from rest_framework import serializers
from djoser.serializers import UserLoginSerializer


class LoginSerializer(UserLoginSerializer):
    client = serializers.CharField()

    class Meta(UserLoginSerializer.Meta):
        fields = UserLoginSerializer.Meta.fields + ('client',)