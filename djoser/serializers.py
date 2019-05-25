import warnings

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError

from djoser import utils
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            settings.LOGIN_FIELD,
        )
        read_only_fields = (settings.LOGIN_FIELD,)

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super(UserSerializer, self).update(instance, validated_data)


class CurrentUserSerializer(UserSerializer):
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
        'cannot_create_user': settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR,
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD, User._meta.pk.name, 'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError({
                'password': serializer_error['non_field_errors']
            })

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


class UserCreatePasswordRetypeSerializer(UserCreateSerializer):
    default_error_messages = {
        'password_mismatch': settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super(UserCreatePasswordRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_password'] = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        re_password = attrs.pop('re_password')
        attrs = super(UserCreatePasswordRetypeSerializer, self).validate(attrs)
        if attrs['password'] == re_password:
            return attrs
        else:
            self.fail('password_mismatch')


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False, style={'input_type': 'password'}
    )

    default_error_messages = {
        'invalid_credentials': settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        'inactive_account': settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super(TokenCreateSerializer, self).__init__(*args, **kwargs)
        self.user = None
        self.fields[settings.LOGIN_FIELD] = serializers.CharField(
            required=False
        )

    def validate(self, attrs):
        self.user = authenticate(
            username=attrs.get(settings.LOGIN_FIELD),
            password=attrs.get('password')
        )

        self._validate_user_exists(self.user)
        return attrs

    def _validate_user_exists(self, user):
        if not user:
            self.fail('invalid_credentials')


class PasswordResetSerializer(serializers.Serializer):
    default_error_messages = {'email_not_found': settings.CONSTANTS.messages.EMAIL_NOT_FOUND}

    def __init__(self, *args, **kwargs):
        super(PasswordResetSerializer, self).__init__(*args, **kwargs)

        email_field = get_user_email_field_name(User)
        self.fields[email_field] = serializers.EmailField()
        validate_email_fn_name = 'validate_' + email_field

        def validate_email_fn(self, value):
            users = self.context['view'].get_users(value)
            if settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND and not users:
                self.fail('email_not_found')
            else:
                return value

        setattr(PasswordResetSerializer, validate_email_fn_name, validate_email_fn)


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': settings.CONSTANTS.messages.INVALID_TOKEN_ERROR,
        'invalid_uid': settings.CONSTANTS.messages.INVALID_UID_ERROR,
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
            key_error = 'invalid_token'
            raise ValidationError({'token': [self.error_messages[key_error]]}, code=key_error)


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {'stale_token': settings.CONSTANTS.messages.STALE_TOKEN_ERROR}

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
        'password_mismatch': settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR,
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
        'invalid_password': settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR,
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
        fields = (settings.LOGIN_FIELD, 'current_password')

    def __init__(self, *args, **kwargs):
        super(SetUsernameSerializer, self).__init__(*args, **kwargs)
        self.username_field = settings.LOGIN_FIELD
        self._default_username_field = self.Meta.model.USERNAME_FIELD
        self.fields['new_' + self.username_field] = self.fields.pop(self.username_field)

    def save(self, **kwargs):
        if self.username_field != self._default_username_field:
            kwargs[User.USERNAME_FIELD] = self.validated_data.get('new_' + self.username_field)
        return super(SetUsernameSerializer, self).save(**kwargs)


class SetUsernameRetypeSerializer(SetUsernameSerializer):
    default_error_messages = {
        'username_mismatch': settings.CONSTANTS.messages.USERNAME_MISMATCH_ERROR.format(
            settings.LOGIN_FIELD
        ),
    }

    def __init__(self, *args, **kwargs):
        super(SetUsernameRetypeSerializer, self).__init__(*args, **kwargs)
        self.fields['re_new_' + settings.LOGIN_FIELD] = serializers.CharField()

    def validate(self, attrs):
        attrs = super(SetUsernameRetypeSerializer, self).validate(attrs)
        new_username = attrs[settings.LOGIN_FIELD]
        if new_username != attrs['re_new_' + settings.LOGIN_FIELD]:
            self.fail('username_mismatch')
        else:
            return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ('auth_token',)
