"""
Custom serializers that test_serializer_settings.py names in DJOSER["SERIALIZERS"].

Each class subclasses djoser's default serializer for one SERIALIZERS key, the way a
project customises djoser, and appends itself to ``SEEN`` when it is instantiated.
A test can then tell which key served a request and what the serializer was given.
The serializers that render response bodies also add a ``marker`` field naming
their key.
"""

from rest_framework import serializers

from djoser import serializers as djoser_serializers
from djoser.social import serializers as social_serializers

SEEN = []


class Spy:
    spy_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SEEN.append(self)


class ActivationSpy(Spy, djoser_serializers.ActivationSerializer):
    spy_key = "activation"


class PasswordResetSpy(Spy, djoser_serializers.SendEmailResetSerializer):
    spy_key = "password_reset"


class PasswordResetConfirmSpy(Spy, djoser_serializers.PasswordResetConfirmSerializer):
    spy_key = "password_reset_confirm"


class PasswordResetConfirmRetypeSpy(
    Spy, djoser_serializers.PasswordResetConfirmRetypeSerializer
):
    spy_key = "password_reset_confirm_retype"


class SetPasswordSpy(Spy, djoser_serializers.SetPasswordSerializer):
    spy_key = "set_password"


class SetPasswordRetypeSpy(Spy, djoser_serializers.SetPasswordRetypeSerializer):
    spy_key = "set_password_retype"


class SetUsernameSpy(Spy, djoser_serializers.SetUsernameSerializer):
    spy_key = "set_username"


class SetUsernameRetypeSpy(Spy, djoser_serializers.SetUsernameRetypeSerializer):
    spy_key = "set_username_retype"


class UsernameResetSpy(Spy, djoser_serializers.SendEmailResetSerializer):
    spy_key = "username_reset"


class UsernameResetConfirmSpy(Spy, djoser_serializers.UsernameResetConfirmSerializer):
    spy_key = "username_reset_confirm"


class UsernameResetConfirmRetypeSpy(
    Spy, djoser_serializers.UsernameResetConfirmRetypeSerializer
):
    spy_key = "username_reset_confirm_retype"


class UserCreateSpy(Spy, djoser_serializers.UserCreateSerializer):
    spy_key = "user_create"
    marker = serializers.SerializerMethodField()

    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = (*djoser_serializers.UserCreateSerializer.Meta.fields, "marker")

    def get_marker(self, obj):
        return self.spy_key


class UserCreatePasswordRetypeSpy(
    Spy, djoser_serializers.UserCreatePasswordRetypeSerializer
):
    spy_key = "user_create_password_retype"


class UserDeleteSpy(Spy, djoser_serializers.UserDeleteSerializer):
    spy_key = "user_delete"


class UserSpy(Spy, djoser_serializers.UserSerializer):
    spy_key = "user"
    marker = serializers.SerializerMethodField()

    class Meta(djoser_serializers.UserSerializer.Meta):
        fields = (*djoser_serializers.UserSerializer.Meta.fields, "marker")

    def get_marker(self, obj):
        return self.spy_key


class CurrentUserSpy(UserSpy):
    spy_key = "current_user"


class TokenSpy(Spy, djoser_serializers.TokenSerializer):
    spy_key = "token"
    marker = serializers.SerializerMethodField()

    class Meta(djoser_serializers.TokenSerializer.Meta):
        fields = (*djoser_serializers.TokenSerializer.Meta.fields, "marker")

    def get_marker(self, obj):
        return self.spy_key


class TokenCreateSpy(Spy, djoser_serializers.TokenCreateSerializer):
    spy_key = "token_create"


class ProviderAuthSpy(Spy, social_serializers.ProviderAuthSerializer):
    spy_key = "provider_auth"


class ViewObjectUserSerializer(djoser_serializers.UserSerializer):
    """
    Renders the pk of ``view.get_object()``, as serializers that look at the object
    being served do.
    """

    view_object = serializers.SerializerMethodField()

    class Meta(djoser_serializers.UserSerializer.Meta):
        fields = (*djoser_serializers.UserSerializer.Meta.fields, "view_object")

    def get_view_object(self, obj):
        return self.context["view"].get_object().pk
