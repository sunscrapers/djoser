from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils import six
from django.utils.module_loading import import_string

from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from . import constants, utils, settings


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
        )
        read_only_fields = (
            User.USERNAME_FIELD,
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True,
                                     validators=settings.get('PASSWORD_VALIDATORS'))

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            User._meta.pk.name,
            'password',
        )

    def create(self, validated_data):
        if settings.get('SEND_ACTIVATION_EMAIL'):
            with transaction.atomic():
                user = User.objects.create_user(**validated_data)
                user.is_active = False
                user.save(update_fields=['is_active'])
        else:
            user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, style={'input_type': 'password'})

    default_error_messages = {
        'inactive_account': constants.INACTIVE_ACCOUNT_ERROR,
        'invalid_credentials': constants.INVALID_CREDENTIALS_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField(required=False)

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get(User.USERNAME_FIELD), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'])


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {
        'email_not_found': constants.EMAIL_NOT_FOUND
    }

    def validate_email(self, value):
        if settings.get('PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND') and \
                not self.context['view'].get_users(value):
            raise serializers.ValidationError(self.error_messages['email_not_found'])
        return value


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': constants.INVALID_TOKEN_ERROR,
        'invalid_uid': constants.INVALID_UID_ERROR,
    }

    def validate_uid(self, value):
        try:
            uid = utils.decode_uid(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError) as error:
            raise serializers.ValidationError(self.error_messages['invalid_uid'])
        return value

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        if not self.context['view'].token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError(self.error_messages['invalid_token'])
        return attrs


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {
        'stale_token': constants.STALE_TOKEN_ERROR,
    }

    def validate(self, attrs):
        attrs = super(ActivationSerializer, self).validate(attrs)
        if self.user.is_active:
            raise exceptions.PermissionDenied(self.error_messages['stale_token'])
        return attrs


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'},
                                         validators=settings.get('PASSWORD_VALIDATORS'))


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'password_mismatch': constants.PASSWORD_MISMATCH_ERROR,
    }

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError(self.error_messages['password_mismatch'])
        return attrs


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': constants.INVALID_PASSWORD_ERROR,
    }

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(self.error_messages['invalid_password'])
        return value


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class SetPasswordRetypeSerializer(PasswordRetypeSerializer, CurrentPasswordSerializer):
    pass


class PasswordResetConfirmSerializer(UidAndTokenSerializer, PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(UidAndTokenSerializer, PasswordRetypeSerializer):
    pass


class SetUsernameSerializer(serializers.ModelSerializer, CurrentPasswordSerializer):

    class Meta(object):
        model = User
        fields = (
            User.USERNAME_FIELD,
            'current_password',
        )

    def __init__(self, *args, **kwargs):
        super(SetUsernameSerializer, self).__init__(*args, **kwargs)
        self.fields['new_' + User.USERNAME_FIELD] = self.fields[User.USERNAME_FIELD]
        del self.fields[User.USERNAME_FIELD]


class SetUsernameRetypeSerializer(SetUsernameSerializer):
    default_error_messages = {
        'username_mismatch': constants.USERNAME_MISMATCH_ERROR.format(User.USERNAME_FIELD),
    }

    def __init__(self, *args, **kwargs):
        super(SetUsernameRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_new_' + User.USERNAME_FIELD] = serializers.CharField()

    def validate(self, attrs):
        attrs = super(SetUsernameRetypeSerializer, self).validate(attrs)
        new_username = attrs[User.USERNAME_FIELD]
        if new_username != attrs['re_new_' + User.USERNAME_FIELD]:
            raise serializers.ValidationError(self.error_messages['username_mismatch'].format(User.USERNAME_FIELD))
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = (
            'auth_token',
        )


class SerializersManager(object):
    def __init__(self, serializer_confs):
        self.serializers = serializer_confs.copy()

    def get(self, serializer_name):
        try:
            if isinstance(self.serializers[serializer_name], six.string_types):
                self.serializers[serializer_name] = self.load_serializer(
                    self.serializers[serializer_name])
            return self.serializers[serializer_name]
        except KeyError:
            raise Exception("Try to use serializer name '%s' that is not one of: %s" % (
                serializer_name,
                tuple(settings.get('SERIALIZERS').keys())
            ))

    def load_serializer(self, serializer_class):
        return import_string(serializer_class)

serializers_manager = SerializersManager(settings.get('SERIALIZERS'))
