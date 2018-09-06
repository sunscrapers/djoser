import warnings

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction

from rest_framework import exceptions, serializers

from djoser import constants, utils
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
        )
        read_only_fields = (User.USERNAME_FIELD,)

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super(UserSerializer, self).update(instance, validated_data)


class CurrentUserSerializer(settings.SERIALIZERS.user):
    def __init__(self, *args, **kwargs):
        # Warn user about serializer split
        warnings.simplefilter('default')
        warnings.warn(
            (
                'Current user endpoints now use their own serializer setting. '
                'For more information, see: '
                'https://djoser.readthedocs.io/en/latest/settings.html#serializers'  # noqa
            ),
            DeprecationWarning,
        )

        # Perform regular init actions
        super(CurrentUserSerializer, self).__init__(*args, **kwargs)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    default_error_messages = {
        'cannot_create_user': constants.CANNOT_CREATE_USER_ERROR,
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD, User._meta.pk.name, 'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail('cannot_create_user')

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=['is_active'])
        return user


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
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField(
            required=False
        )

    def validate(self, attrs):
        self.user = authenticate(
            username=attrs.get(User.USERNAME_FIELD),
            password=attrs.get('password')
        )

        self._validate_user_exists(self.user)
        self._validate_user_is_active(self.user)
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
        users = self.context['view'].get_users(value)
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

    def validate_uid(self, value):
        try:
            uid = utils.decode_uid(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            self.fail('invalid_uid')

        return value

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        is_token_valid = self.context['view'].token_generator.check_token(
            self.user, attrs['token']
        )
        if is_token_valid:
            return attrs
        else:
            self.fail('invalid_token')


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {'stale_token': constants.STALE_TOKEN_ERROR}

    def validate(self, attrs):
        attrs = super(ActivationSerializer, self).validate(attrs)
        if not self.user.is_active:
            return attrs
        raise exceptions.PermissionDenied(self.error_messages['stale_token'])


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


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class SetPasswordRetypeSerializer(PasswordRetypeSerializer,
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


class SetUsernameSerializer(serializers.ModelSerializer,
                            CurrentPasswordSerializer):

    class Meta(object):
        model = User
        fields = (User.USERNAME_FIELD, 'current_password')

    def __init__(self, *args, **kwargs):
        """
        This method should probably be replaced by a better solution.
        Its purpose is to replace USERNAME_FIELD with 'new_' + USERNAME_FIELD
        so that the new field is being assigned a field for USERNAME_FIELD
        """
        super(SetUsernameSerializer, self).__init__(*args, **kwargs)
        username_field = User.USERNAME_FIELD
        self.fields['new_' + username_field] = self.fields.pop(username_field)


class SetUsernameRetypeSerializer(SetUsernameSerializer):
    default_error_messages = {
        'username_mismatch': constants.USERNAME_MISMATCH_ERROR.format(
            User.USERNAME_FIELD
        ),
    }

    def __init__(self, *args, **kwargs):
        super(SetUsernameRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_new_' + User.USERNAME_FIELD] = serializers.CharField()

    def validate(self, attrs):
        attrs = super(SetUsernameRetypeSerializer, self).validate(attrs)
        new_username = attrs[User.USERNAME_FIELD]
        if new_username != attrs['re_new_' + User.USERNAME_FIELD]:
            self.fail('username_mismatch')
        else:
            return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ('auth_token',)
