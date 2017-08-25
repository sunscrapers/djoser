from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.reverse import reverse

from djoser.conf import settings
from djoser.compat import get_user_email_field_name

from . import utils, signals

User = get_user_model()


class RootView(views.APIView):
    """
    Root endpoint - use one of sub endpoints.
    """
    permission_classes = (
        permissions.AllowAny,
    )
    urls_mapping = {
        'me': 'user',
        'register': 'register',
        'activate': 'activate',
        'change-' + User.USERNAME_FIELD: 'set_username',
        'change-password': 'set_password',
        'password-reset': 'password_reset',
        'password-reset-confirm': 'password_reset_confirm',
    }
    urls_extra_mapping = None

    def get_urls_mapping(self, **kwargs):
        mapping = self.urls_mapping.copy()
        mapping.update(kwargs)
        if self.urls_extra_mapping:
            mapping.update(self.urls_extra_mapping)
        mapping.update(settings.ROOT_VIEW_URLS_MAPPING)
        return mapping

    def get(self, request, format=None):
        return Response(
            dict([(key, reverse(url_name, request=request, format=format))
                  for key, url_name in self.get_urls_mapping().items()])
        )


class RegistrationView(generics.CreateAPIView):
    """
    Use this endpoint to register new user.
    """
    serializer_class = settings.SERIALIZERS.user_registration
    permission_classes = (
        permissions.AllowAny,
    )

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        email_factory_cls = None
        if settings.SEND_ACTIVATION_EMAIL:
            email_factory_cls = utils.UserActivationEmailFactory
        elif settings.SEND_CONFIRMATION_EMAIL:
            email_factory_cls = utils.UserConfirmationEmailFactory

        if email_factory_cls is not None:
            utils.send_email(self.request, email_factory_cls, user)


class LoginView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """
    serializer_class = settings.SERIALIZERS.login
    permission_classes = (
        permissions.AllowAny,
    )

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_200_OK,
        )


class LogoutView(views.APIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to send email to user with password reset link.
    """
    serializer_class = settings.SERIALIZERS.password_reset
    permission_classes = (
        permissions.AllowAny,
    )

    _users = None

    def _action(self, serializer):
        for user in self.get_users(serializer.data['email']):
            self.send_password_reset_email(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_users(self, email):
        if self._users is None:
            email_field_name = get_user_email_field_name(User)
            users = User._default_manager.filter(**{
                email_field_name + '__iexact': email
            })
            self._users = [
                u for u in users if u.is_active and u.has_usable_password()
            ]
        return self._users

    def send_password_reset_email(self, user):
        email_factory = utils.UserPasswordResetEmailFactory.from_request(
            self.request, user=user
        )
        email = email_factory.create()
        email.send()


class SetPasswordView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to change user password.
    """
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer_class(self):
        if settings.SET_PASSWORD_RETYPE:
            return settings.SERIALIZERS.set_password_retype
        return settings.SERIALIZERS.set_password

    def _action(self, serializer):
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to finish reset password process.
    """
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def get_serializer_class(self):
        if settings.PASSWORD_RESET_CONFIRM_RETYPE:
            return settings.SERIALIZERS.password_reset_confirm_retype
        return settings.SERIALIZERS.password_reset_confirm

    def _action(self, serializer):
        serializer.user.set_password(serializer.data['new_password'])
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivationView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to activate user account.
    """
    serializer_class = settings.SERIALIZERS.activation
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def _action(self, serializer):
        serializer.user.is_active = True
        serializer.user.save()
        signals.user_activated.send(
            sender=self.__class__, user=serializer.user, request=self.request)

        if settings.SEND_CONFIRMATION_EMAIL:
            email_factory = utils.UserConfirmationEmailFactory.from_request(
                self.request, user=serializer.user)
            email = email_factory.create()
            email.send()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetUsernameView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to change user username.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if settings.SET_USERNAME_RETYPE:
            return settings.SERIALIZERS.set_username_retype
        return settings.SERIALIZERS.set_username

    def _action(self, serializer):
        user = self.request.user
        new_username = serializer.data['new_' + User.USERNAME_FIELD]

        setattr(user, User.USERNAME_FIELD, new_username)
        if settings.SEND_ACTIVATION_EMAIL:
            user.is_active = False
            email_factory_cls = utils.UserActivationEmailFactory
            utils.send_email(self.request, email_factory_cls, user)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserView(generics.RetrieveUpdateAPIView):
    """
    Use this endpoint to retrieve/update user.
    """
    model = User
    serializer_class = settings.SERIALIZERS.user
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, *args, **kwargs):
        return self.request.user

    def perform_update(self, serializer):
        super(UserView, self).perform_update(serializer)
        user = serializer.instance
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            email_factory_cls = utils.UserActivationEmailFactory
            utils.send_email(self.request, email_factory_cls, user)
