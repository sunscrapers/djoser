from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from . import constants

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )
        write_only_fields = (
            'password',
        )

    def save(self, **kwargs):
        return User.objects.create_user(**self.init_data.dict())


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            'password',
        )
        write_only_fields = (
            'password',
        )

    def validate(self, attrs):
        self.object = authenticate(username=attrs[User.USERNAME_FIELD], password=attrs['password'])
        if self.object:
            if not self.object.is_active:
                raise serializers.ValidationError(constants.DISABLE_ACCOUNT_ERROR)
            return attrs
        else:
            raise serializers.ValidationError(constants.INVALID_CREDENTIALS_ERROR)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate_uid(self, attrs, source):
        value = attrs[source]
        try:
            uid = urlsafe_base64_decode(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, ValueError, OverflowError) as error:
            raise serializers.ValidationError(error)
        return attrs

    def validate(self, attrs):
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError(constants.INVALID_TOKEN_ERROR)
        return attrs
