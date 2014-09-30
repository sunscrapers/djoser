from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from rest_framework import generics, permissions, status, response
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
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


class FormWrapperAPIView(generics.GenericAPIView):

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            form = self.form_class(**self.get_form_kwargs(serializer))
            if form.is_valid():
                form.save(**self.get_form_save_kwargs())
                return response.Response(status=status.HTTP_200_OK)
            else:
                return response.Response(
                    data=dict(form.errors),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_form_kwargs(self, serializer):
        return {
            'data': serializer.data,
        }

    def get_form_save_kwargs(self):
        return {}


class PasswordResetView(FormWrapperAPIView):
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    form_class = PasswordResetForm

    def get_form_save_kwargs(self):
        return {
            'request': self.request,
            'use_https': self.request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
        }


class SetPasswordView(FormWrapperAPIView):
    serializer_class = serializers.SetPasswordSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    form_class = SetPasswordForm

    def get_form_kwargs(self, serializer):
        return {
            'user': serializer.user,
            'data': serializer.data,
        }