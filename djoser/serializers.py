from distutils import version
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
import rest_framework
from rest_framework.authtoken.models import Token
from . import constants, utils

User = get_user_model()


def create_username_field():
    username_field = User._meta.get_field(User.USERNAME_FIELD)
    if hasattr(serializers.ModelSerializer, 'field_mapping'):  # DRF 2.x
        mapping_dict = serializers.ModelSerializer.field_mapping
    elif hasattr(serializers.ModelSerializer, '_field_mapping'):  # DRF 3.0
        mapping_dict = serializers.ModelSerializer._field_mapping.mapping
    elif hasattr(serializers.ModelSerializer, 'serializer_field_mapping'):  # DRF 3.1
        mapping_dict = serializers.ModelSerializer.serializer_field_mapping
    else:
        raise AttributeError(
            'serializers.ModelSerializer doesn\'t have any of these attributes: '
            'field_mapping, _field_mapping, serializer_field_mapping '
        )
    field_class = mapping_dict[username_field.__class__]
    return field_class()


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


class AbstractUserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            User._meta.pk.name,
            'password',
        )
        write_only_fields = (
            'password',
        )

if version.StrictVersion(rest_framework.VERSION) >= version.StrictVersion('3.0.0'):

    class UserRegistrationSerializer(AbstractUserRegistrationSerializer):

        def create(self, validated_data):
            return User.objects.create_user(**validated_data)

else:

    class UserRegistrationSerializer(AbstractUserRegistrationSerializer):

        def restore_object(self, attrs, instance=None):
            try:
                return User.objects.get(**{User.USERNAME_FIELD: attrs[User.USERNAME_FIELD]})
            except User.DoesNotExist:
                return User.objects.create_user(**attrs)

        def save_object(self, obj, **kwargs):
            return obj


class UserRegistrationWithAuthTokenSerializer(UserRegistrationSerializer):
    auth_token = serializers.SerializerMethodField(method_name='get_user_auth_token')

    class Meta(UserRegistrationSerializer.Meta):
        model = User
        fields = UserRegistrationSerializer.Meta.fields + (
            'auth_token',
        )

    def get_user_auth_token(self, obj):
        return obj.auth_token.key


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)

    default_error_messages = {
        'inactive_account': constants.INACTIVE_ACCOUNT_ERROR,
        'invalid_credentials': constants.INVALID_CREDENTIALS_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField(required=False)

    def validate(self, attrs):
        self.user = authenticate(username=attrs[User.USERNAME_FIELD], password=attrs['password'])
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'])


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': constants.INVALID_TOKEN_ERROR
    }

    def validate_uid(self, attrs_or_value, source=None):
        value = attrs_or_value[source] if source else attrs_or_value
        try:
            uid = utils.decode_uid(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, ValueError, OverflowError) as error:
            raise serializers.ValidationError(error)
        return attrs_or_value

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        if not self.context['view'].token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError(self.error_messages['invalid_token'])
        return attrs


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField()

    default_error_messages = {
        'password_mismatch': constants.PASSWORD_MISMATCH_ERROR,
    }

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError(self.error_messages['password_mismatch'])
        return attrs


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()

    default_error_messages = {
        'invalid_password': constants.INVALID_PASSWORD_ERROR,
    }

    def validate_current_password(self, attrs_or_value, source=None):
        value = attrs_or_value[source] if source else attrs_or_value
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(self.error_messages['invalid_password'])
        return attrs_or_value


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
        if User.USERNAME_FIELD in attrs:
            new_username = attrs[User.USERNAME_FIELD]
        else:  # DRF 2.4
            new_username = attrs['new_' + User.USERNAME_FIELD]
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
