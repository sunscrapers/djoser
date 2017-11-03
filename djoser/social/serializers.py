from rest_framework import serializers

from social_core import exceptions
from social_django.utils import load_backend, load_strategy

from djoser.conf import settings


class ProviderAuthSerializer(serializers.Serializer):
    # GET auth token
    token = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    # POST OAuth/OpenID values
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(required=False, write_only=True)

    def create(self, validated_data):
        user = validated_data['user']
        return settings.SOCIAL_AUTH_TOKEN_STRATEGY.obtain(user)

    def validate_state(self, value):
        strategy = load_strategy(self.context['request'])
        redirect_uri = strategy.session_get('redirect_uri')

        backend_name = self.context['view'].kwargs['provider']
        backend = load_backend(
            strategy, backend_name, redirect_uri=redirect_uri
        )

        try:
            backend.validate_state()
        except exceptions.AuthException:
            raise serializers.ValidationError('State could not be verified.')

    def validate(self, attrs):
        strategy = load_strategy(self.context['request'])
        redirect_uri = strategy.session_get('redirect_uri')

        backend_name = self.context['view'].kwargs['provider']
        backend = load_backend(
            strategy, backend_name, redirect_uri=redirect_uri
        )

        try:
            user = backend.auth_complete()
        except exceptions.AuthException:
            raise serializers.ValidationError(
                'Failed to finish authentication.'
            )
        return {'user': user}
