from rest_framework import serializers
from social_core import exceptions
from social_django.utils import load_backend, load_strategy

from djoser.conf import settings


class ProviderAuthSerializer(serializers.Serializer):
    # GET auth token
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = validated_data["user"]
        return settings.SOCIAL_AUTH_TOKEN_STRATEGY.obtain(user)

    def validate(self, attrs):
        request = self.context["request"]
        if "state" in request.GET:
            self._validate_state(request.GET["state"])

        strategy = load_strategy(request)
        redirect_uri = strategy.session_get("redirect_uri")

        backend_name = self.context["view"].kwargs["provider"]
        backend = load_backend(strategy, backend_name, redirect_uri=redirect_uri)

        try:
            user = backend.auth_complete()
        except exceptions.AuthException as e:
            raise serializers.ValidationError(str(e))
        return {"user": user}

    def _validate_state(self, value):
        request = self.context["request"]
        strategy = load_strategy(request)
        redirect_uri = strategy.session_get("redirect_uri")

        backend_name = self.context["view"].kwargs["provider"]
        backend = load_backend(strategy, backend_name, redirect_uri=redirect_uri)

        try:
            backend.validate_state()
        except exceptions.AuthMissingParameter:
            raise serializers.ValidationError(
                "State could not be found in request data."
            )
        except exceptions.AuthStateMissing:
            raise serializers.ValidationError(
                "State could not be found in server-side session data."
            )
        except exceptions.AuthStateForbidden:
            raise serializers.ValidationError("Invalid state has been provided.")

        return value
