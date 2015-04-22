from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, response
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.tokens import default_token_generator
from . import serializers, settings, utils

User = get_user_model()


class RootView(generics.GenericAPIView):
    """
    Root endpoint - use one of sub endpoints.
    """

    def get(self, request, format=None):
        urls_mapping = {
            'me': 'user',
            'register': 'register',
            'login': 'login',
            'logout': 'logout',
            'activate': 'activate',
            'change-' + User.USERNAME_FIELD: 'set_username',
            'change-password': 'set_password',
            'password-reset': 'password_reset',
            'password-reset-confirm': 'password_reset_confirm',
        }

        return Response(
            dict([(key, reverse(url_name, request=request, format=format))
                  for key, url_name in urls_mapping.items()])
        )


class RegistrationView(utils.SendEmailViewMixin, generics.CreateAPIView):
    """
    Use this endpoint to register new user.
    """
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator
    serializer_class = serializers.UserRegistrationSerializer

    def post_save(self, obj, created=False):
        if settings.get('SEND_ACTIVATION_EMAIL'):
            self.send_email(**self.get_send_email_kwargs(obj))

    def perform_create(self, serializer):
        instance = serializer.save()
        self.post_save(obj=instance, created=True)

    def get_send_email_extras(self):
        return {
            'subject_template_name': 'activation_email_subject.txt',
            'plain_body_template_name': 'activation_email_body.txt',
        }

    def get_email_context(self, user):
        context = super(RegistrationView, self).get_email_context(user)
        context['url'] = settings.get('ACTIVATION_URL').format(**context)
        return context


class LoginView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """
    permission_classes = (
        permissions.AllowAny,
    )

    def action(self, serializer):
        token = utils.get_or_create_token(user=serializer.object, serializer_data=serializer.data)
        return Response(
            data=serializers.TokenSerializer(token).data,
            status=status.HTTP_200_OK,
        )

    def get_serializer_class(self):
        return utils.get_login_serializer()


class LogoutView(generics.GenericAPIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        if request.auth:
            request.auth.delete()
        return response.Response(status=status.HTTP_200_OK)


class PasswordResetView(utils.ActionViewMixin, utils.SendEmailViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to send email to user with password reset link.
    """
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def action(self, serializer):
        for user in self.get_users(serializer.data['email']):
            self.send_email(**self.get_send_email_kwargs(user))
        return response.Response(status=status.HTTP_200_OK)

    def get_users(self, email):
        active_users = User._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.has_usable_password())

    def get_send_email_extras(self):
        return {
            'subject_template_name': 'password_reset_email_subject.txt',
            'plain_body_template_name': 'password_reset_email_body.txt',
        }

    def get_email_context(self, user):
        context = super(PasswordResetView, self).get_email_context(user)
        context['url'] = settings.get('PASSWORD_RESET_CONFIRM_URL').format(**context)
        return context


class SetPasswordView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to change user password.
    """
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer_class(self):
        if settings.get('SET_PASSWORD_RETYPE'):
            return serializers.SetPasswordRetypeSerializer
        return serializers.SetPasswordSerializer

    def action(self, serializer):
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return response.Response(status=status.HTTP_200_OK)


class PasswordResetConfirmView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to finish reset password process.
    """
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def get_serializer_class(self):
        if settings.get('PASSWORD_RESET_CONFIRM_RETYPE'):
            return serializers.PasswordResetConfirmRetypeSerializer
        return serializers.PasswordResetConfirmSerializer

    def action(self, serializer):
        serializer.user.set_password(serializer.data['new_password'])
        serializer.user.save()
        return response.Response(status=status.HTTP_200_OK)


class ActivationView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to activate user account.
    """
    serializer_class = serializers.UidAndTokenSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def action(self, serializer):
        serializer.user.is_active = True
        serializer.user.save()
        return Response(status=status.HTTP_200_OK)


class SetUsernameView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to change user username.
    """
    serializer_class = serializers.SetUsernameSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer_class(self):
        if settings.get('SET_USERNAME_RETYPE'):
            return serializers.SetUsernameRetypeSerializer
        return serializers.SetUsernameSerializer

    def action(self, serializer):
        setattr(self.request.user, User.USERNAME_FIELD, serializer.data['new_' + User.USERNAME_FIELD])
        self.request.user.save()
        return response.Response(status=status.HTTP_200_OK)


class UserView(generics.RetrieveUpdateAPIView):
    """
    Use this endpoint to retrieve/update user.
    """
    model = User
    serializer_class = serializers.UserSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_object(self, *args, **kwargs):
        return self.request.user

