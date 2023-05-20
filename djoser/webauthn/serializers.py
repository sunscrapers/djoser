from django.contrib.auth import get_user_model
from rest_framework import serializers

from djoser.conf import settings
from djoser.serializers import UserCreateMixin

from .models import CredentialOptions
from .utils import create_challenge, create_ukey

User = get_user_model()


class WebauthnSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialOptions
        fields = ("username", "display_name")

    def create(self, validated_data):
        validated_data.update(
            {
                "challenge": create_challenge(
                    length=settings.WEBAUTHN["CHALLENGE_LENGTH"]
                ),
                "ukey": create_ukey(length=settings.WEBAUTHN["UKEY_LENGTH"]),
            }
        )
        return super().create(validated_data)

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(f"User {username} already exists.")
        return username


class WebauthnCreateUserSerializer(UserCreateMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            User._meta.pk.name,
        )


class WebauthnLoginSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[settings.LOGIN_FIELD] = serializers.CharField(required=True)

    def validate_username(self, username):
        try:
            search_kwargs = {
                settings.LOGIN_FIELD: username,
                "credential_options__isnull": False,
            }
            self.user = user = User.objects.get(**search_kwargs)
        except User.DoesNotExist:
            self.fail("invalid_credentials")

        if not user.is_active:
            self.fail("invalid_credentials")

        return username
