from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status, response
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from . import serializers


class RegistrationView(generics.CreateAPIView):
    serializer_class = serializers.UserRegistrationSerializer
    permission_classes = (
        permissions.AllowAny,
    )


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
                data={'token': token.key},
                status=status.HTTP_200_OK,
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetView(generics.GenericAPIView):
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
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.has_usable_password())

    def get_email_context(self, user):
        return {
            'user': user,
            'domain': settings.DJOSER['DOMAIN'],
            'url': settings.DJOSER['PASSWORD_RESET_CONFIRM_URL'],
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': self.token_generator.make_token(user),
            'protocol': self.request.is_secure(),
        }

    def get_send_email_kwargs(self, user):
        return {
            'subject_template_name': 'registration/password_reset_subject.txt',
            'email_template_name': 'registration/password_reset_email.html',
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'to_email': user.email,
        }

    def send_email(self, subject_template_name, email_template_name,
                   context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            serializer.user.set_password(serializer.data['new_password1'])
            serializer.user.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
