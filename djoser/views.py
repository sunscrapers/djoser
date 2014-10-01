from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status, response
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from . import serializers, settings, emails

User = get_user_model()


class SendEmailViewMixin(object):

    def get_send_email_kwargs(self, user):
        return {
            'from_email': getattr(django_settings, 'DEFAULT_FROM_EMAIL', None),
            'to_email': user.email,
        }

    def send_email(self, **kwargs):
        emails.send(**kwargs)

    def get_email_context(self, user):
        token = self.token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = settings.get('ACTIVATION_URL').format(uid=uid, token=token)
        return {
            'user': user,
            'domain': settings.get('DOMAIN'),
            'site_name': settings.get('SITE_NAME'),
            'url': url,
            'uid': uid,
            'token': token,
            'protocol': 'https' if self.request.is_secure() else 'http',
        }


class RegistrationView(SendEmailViewMixin, generics.CreateAPIView):
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def get_serializer_class(self):
        if settings.get('LOGIN_AFTER_REGISTRATION'):
            return serializers.UserRegistrationWithAuthTokenSerializer
        return serializers.UserRegistrationSerializer

    def post_save(self, obj, created=False):
        if settings.get('LOGIN_AFTER_REGISTRATION'):
            Token.objects.get_or_create(user=obj)
        if settings.get('SEND_ACTIVATION_EMAIL'):
            self.send_email(
                context=self.get_email_context(obj),
                **self.get_send_email_kwargs(obj)
            )

    def get_send_email_kwargs(self, user):
        context = super(RegistrationView, self).get_send_email_kwargs(user)
        context.update({
            'subject_template_name': 'activation_email_subject.txt',
            'plain_body_template_name': 'activation_email_body.txt',
        })
        return context

    def get_email_context(self, user):
        context = super(RegistrationView, self).get_email_context(user)
        context['url'] = settings.get('ACTIVATION_URL').format(**context)
        return context


class LoginView(generics.GenericAPIView):
    serializer_class = serializers.UserLoginSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, _ = Token.objects.get_or_create(user=serializer.object)
            return Response(
                data=serializers.TokenSerializer(token).data,
                status=status.HTTP_200_OK,
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetView(SendEmailViewMixin, generics.GenericAPIView):
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            for user in self.get_users(serializer.data['email']):
                self.send_email(
                    context=self.get_email_context(user),
                    **self.get_send_email_kwargs(user)
                )

            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_users(self, email):
        active_users = User._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.has_usable_password())

    def get_send_email_kwargs(self, user):
        context = super(PasswordResetView, self).get_send_email_kwargs(user)
        context.update({
            'subject_template_name': 'password_reset_subject.txt',
            'plain_body_template_name': 'password_reset_email.html',
        })
        return context

    def get_email_context(self, user):
        context = super(PasswordResetView, self).get_email_context(user)
        context['url'] = settings.get('PASSWORD_RESET_CONFIRM_URL').format(**context)
        return context


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def post(self, request):
        serializer = self.serializer_class(
            data=request.DATA,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.user.set_password(serializer.data['new_password1'])
            serializer.user.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class ActivationView(generics.GenericAPIView):
    serializer_class = serializers.UidAndTokenSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    token_generator = default_token_generator

    def post(self, request):
        serializer = self.serializer_class(
            data=request.DATA,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.user.is_active = True
            serializer.user.save()
            if settings.get('LOGIN_AFTER_ACTIVATION'):
                token, _ = Token.objects.get_or_create(user=serializer.user)
                data = serializers.TokenSerializer(token).data
            else:
                data = {}
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetPasswordView(generics.GenericAPIView):
    serializer_class = serializers.SetPasswordSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        serializer = self.serializer_class(
            data=request.DATA,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            request.user.set_password(serializer.data['new_password1'])
            request.user.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetUsernameView(generics.GenericAPIView):
    serializer_class = serializers.SetUsernameSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request):
        serializer = self.serializer_class(
            data=request.DATA,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            setattr(request.user, request.user.USERNAME_FIELD, serializer.data['new_username1'])
            request.user.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )