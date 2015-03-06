from distutils import version
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
import rest_framework
from rest_framework.authtoken.models import Token
from . import constants, utils

User = get_user_model()


def create_username_field():
    username_field = User._meta.get_field(User.USERNAME_FIELD)
    if hasattr(serializers.ModelSerializer, 'field_mapping'):
        mapping_dict = serializers.ModelSerializer.field_mapping
    elif hasattr(serializers.ModelSerializer, '_field_mapping'):
        mapping_dict = serializers.ModelSerializer._field_mapping.mapping
    elif hasattr(serializers.ModelSerializer, 'serializer_field_mapping'):
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


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'password',
        )
        write_only_fields = (
            'password',
        )

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD] = create_username_field()

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


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

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
            raise serializers.ValidationError(constants.INVALID_TOKEN_ERROR)
        return attrs


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField()

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError(constants.PASSWORD_MISMATCH_ERROR)
        return attrs


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()

    def validate_current_password(self, attrs_or_value, source=None):
        value = attrs_or_value[source] if source else attrs_or_value
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(constants.INVALID_PASSWORD_ERROR)
        return attrs_or_value


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class SetPasswordRetypeSerializer(PasswordRetypeSerializer, CurrentPasswordSerializer):
    pass


class PasswordResetConfirmSerializer(UidAndTokenSerializer, PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(UidAndTokenSerializer, PasswordRetypeSerializer):
    pass


class SetUsernameSerializer(CurrentPasswordSerializer):

    def __init__(self, *args, **kwargs):
        super(SetUsernameSerializer, self).__init__(*args, **kwargs)
        self.fields['new_' + User.USERNAME_FIELD] = create_username_field()


class SetUsernameRetypeSerializer(SetUsernameSerializer):

    def __init__(self, *args, **kwargs):
        super(SetUsernameRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_new_' + User.USERNAME_FIELD] = create_username_field()

    def validate(self, attrs):
        attrs = super(SetUsernameRetypeSerializer, self).validate(attrs)
        if attrs['new_' + User.USERNAME_FIELD] != attrs['re_new_' + User.USERNAME_FIELD]:
            raise serializers.ValidationError(constants.USERNAME_MISMATCH_ERROR.format(User.USERNAME_FIELD))
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = (
            'auth_token',
        )