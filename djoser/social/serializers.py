from rest_framework import serializers

from social_core import exceptions
from social_django.utils import load_backend, load_strategy


class ProviderAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(read_only=True)
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(required=False, write_only=True)

    def create(self, validated_data):
        strategy = load_strategy(self.context['request'])
        redirect_uri = strategy.session_get('redirect_uri')

        backend_name = self.context['view'].kwargs['provider']
        backend = load_backend(
            strategy, backend_name, redirect_uri=redirect_uri
        )
        return backend.auth_complete()

    def update(self, instance, validated_data):
        pass

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
