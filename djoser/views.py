from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.reverse import reverse

from djoser.conf import settings
from djoser.compat import get_user_email_field_name

from djoser import utils, signals
from djoser.compat import NoReverseMatch

User = get_user_model()


class RootView(views.APIView):
    """
    Root endpoint - use one of sub endpoints.
    """
    permission_classes = [permissions.AllowAny]

    def aggregate_djoser_urlpattern_names(self):
        from djoser.urls import base, authtoken, jwt
        urlpattern_names = [pattern.name for pattern in base.urlpatterns]
        urlpattern_names += [pattern.name for pattern in authtoken.urlpatterns]
        urlpattern_names += [pattern.name for pattern in jwt.urlpatterns]
        return urlpattern_names

    def get_urls_map(self, request, urlpattern_names, fmt):
        urls_map = {}
        for urlpattern_name in urlpattern_names:
            try:
                url = reverse(urlpattern_name, request=request, format=fmt)
            except NoReverseMatch:
                url = ''
            urls_map[urlpattern_name] = url
        return urls_map

    def get(self, request, fmt=None):
        urlpattern_names = self.aggregate_djoser_urlpattern_names()
        urls_map = self.get_urls_map(request, urlpattern_names, fmt)
        return Response(urls_map)


class RegistrationView(generics.CreateAPIView):
    """
    Use this endpoint to register new user.
    """
    serializer_class = settings.SERIALIZERS.user_registration
    permission_classes = (
        permissions.AllowAny,
    )
    _users = None

    def create(self, request, *args, **kwargs):
        try:
            email_field_name = get_user_email_field_name(User)
            users = self.get_email_users(request.data.get(email_field_name))
            for user in users:
                serializer = self.get_serializer(instance=user)
                if settings.RESEND_REGISTRATION_EMAIL:
                    self.resend_registration_email(user)
                headers = self.get_success_headers(serializer.data)
            if not settings.REGISTRATION_SHOW_EMAIL_FOUND and users:
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except User.DoesNotExist:
            pass
        response = super(RegistrationView, self).create(request, *args, **kwargs)
        return response

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

    def resend_registration_email(self, user):
        if user.is_active:
            email_factory = utils.UserReregistrationEmailFactory.from_request(
                self.request, user=user
            )
        else:
            email_factory = utils.UserReregistrationInactiveEmailFactory.from_request(
                self.request, user=user
            )
        email = email_factory.create()
        email.send()

    def get_email_users(self, email):
        if self._users is None:
            email_field_name = get_user_email_field_name(User)
            email_users_kwargs = {
                email_field_name + '__iexact': email,
            }
            email_users = User._default_manager.filter(**email_users_kwargs)
            self._users = [u for u in email_users if u.has_usable_password()]
        return self._users


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
