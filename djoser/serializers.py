from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions

from rest_framework import serializers

from djoser import constants, utils
from djoser.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            User._meta.pk.name, User.get_email_field_name(),
            User.USERNAME_FIELD
        ]
        read_only_fields = [User.USERNAME_FIELD]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = [User.USERNAME_FIELD, User._meta.pk.name, 'password']

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False, style={'input_type': 'password'}
    )

    default_error_messages = {
        'invalid_credentials': constants.INVALID_CREDENTIALS_ERROR,
        'inactive_account': constants.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super(TokenCreateSerializer, self).__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD] = serializers.CharField(
            required=False
        )

    def validate(self, attrs):
        attrs['user'] = authenticate(
            username=attrs.get(User.USERNAME_FIELD),
            password=attrs.get('password')
        )

        self._validate_user_exists(attrs['user'])
        self._validate_user_is_active(attrs['user'])
        return attrs

    def _validate_user_exists(self, user):
        if not user:
            self.fail('invalid_credentials')

    def _validate_user_is_active(self, user):
        if not user.is_active:
            self.fail('inactive_account')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {'email_not_found': constants.EMAIL_NOT_FOUND}

    def validate_email(self, value):
        users = utils.get_users_for_email(value)
        if settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND and not users:
            self.fail('email_not_found')
        else:
            return value


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': constants.INVALID_TOKEN_ERROR,
        'invalid_uid': constants.INVALID_UID_ERROR,
    }

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        try:
            uid = utils.decode_uid(attrs['uid'])
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            self.fail('invalid_uid')

        is_token_valid = default_token_generator.check_token(
            user, attrs['token']
        )
        if is_token_valid:
            attrs['user'] = user
            return attrs
        else:
            self.fail('invalid_token')


class UserActivateSerializer(UidAndTokenSerializer):
    default_error_messages = {'stale_token': constants.STALE_TOKEN_ERROR}

    def validate(self, attrs):
        attrs = super(UserActivateSerializer, self).validate(attrs)
        if not attrs['user'].is_active:
            return attrs
        raise self.fail('stale_token')


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        user = self.context['request'].user or self.user
        assert user is not None

        try:
            validate_password(attrs['new_password'], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return super(PasswordSerializer, self).validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'password_mismatch': constants.PASSWORD_MISMATCH_ERROR,
    }

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] == attrs['re_new_password']:
            return attrs
        else:
            self.fail('password_mismatch')


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': constants.INVALID_PASSWORD_ERROR,
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail('invalid_password')


class PasswordUpdateSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class PasswordUpdateRetypeSerializer(PasswordRetypeSerializer,
                                  CurrentPasswordSerializer):
    pass


class PasswordResetConfirmSerializer(UidAndTokenSerializer,
                                     PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(UidAndTokenSerializer,
                                           PasswordRetypeSerializer):
    pass


class UserDeleteSerializer(CurrentPasswordSerializer):
    pass


class UsernameUpdateSerializer(serializers.ModelSerializer,
                            CurrentPasswordSerializer):

    class Meta(object):
        model = User
        fields = (User.USERNAME_FIELD, 'current_password')


class UsernameUpdateRetypeSerializer(UsernameUpdateSerializer):
    default_error_messages = {
        'username_mismatch': constants.USERNAME_MISMATCH_ERROR.format(
            User.USERNAME_FIELD
        ),
    }

    def __init__(self, *args, **kwargs):
        super(UsernameUpdateRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_' + User.USERNAME_FIELD] = serializers.CharField()

    def validate(self, attrs):
        attrs = super(UsernameUpdateRetypeSerializer, self).validate(attrs)
        new_username = attrs[User.USERNAME_FIELD]
        if new_username != attrs['re_' + User.USERNAME_FIELD]:
            self.fail('username_mismatch')
        else:
            return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ('auth_token',)
