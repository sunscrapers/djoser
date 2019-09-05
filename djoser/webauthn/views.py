from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from webauthn import (
    WebAuthnAssertionOptions,
    WebAuthnAssertionResponse,
    WebAuthnMakeCredentialOptions,
    WebAuthnRegistrationResponse,
    WebAuthnUser,
)
from webauthn.webauthn import (
    AuthenticationRejectedException,
    RegistrationRejectedException,
)

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.utils import login_user

from .models import CredentialOptions
from .serializers import WebauthnLoginSerializer, WebauthnSignupSerializer
from .utils import create_challenge

User = get_user_model()


class SingupRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = WebauthnSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        co = serializer.save()

        credential_registration_dict = WebAuthnMakeCredentialOptions(
            challenge=co.challenge,
            rp_name=settings.WEBAUTHN["RP_NAME"],
            rp_id=settings.WEBAUTHN["RP_ID"],
            user_id=co.ukey,
            username=co.username,
            display_name=co.display_name,
            icon_url="",
        )

        return Response(credential_registration_dict.registration_dict)


class SignupView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = settings.WEBAUTHN.SIGNUP_SERIALIZER

    def post(self, request, ukey):
        co = get_object_or_404(CredentialOptions, ukey=ukey)
        user_serializer = self.serializer_class(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        webauthn_registration_response = WebAuthnRegistrationResponse(
            rp_id=settings.WEBAUTHN["RP_ID"],
            origin=settings.WEBAUTHN["ORIGIN"],
            registration_response=request.data,
            challenge=co.challenge,
            none_attestation_permitted=True,
        )
        try:
            webauthn_credential = webauthn_registration_response.verify()
        except RegistrationRejectedException:
            return Response(
                {api_settings.NON_FIELD_ERRORS_KEY: "WebAuthn verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = user_serializer.save()
        co.challenge = ""
        co.user = user
        co.sign_count = webauthn_credential.sign_count
        co.credential_id = webauthn_credential.credential_id.decode()
        co.public_key = webauthn_credential.public_key.decode()
        co.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class LoginRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = WebauthnLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        co = CredentialOptions.objects.get(
            username=serializer.validated_data["username"]
        )

        co.challenge = create_challenge(32)
        co.save()

        webauthn_user = WebAuthnUser(
            user_id=co.ukey,
            username=co.username,
            display_name=co.display_name,
            icon_url="",
            credential_id=co.credential_id,
            public_key=co.public_key,
            sign_count=co.sign_count,
            rp_id=settings.WEBAUTHN["RP_ID"],
        )
        webauthn_assertion_options = WebAuthnAssertionOptions(
            webauthn_user, co.challenge
        )

        return Response(webauthn_assertion_options.assertion_dict)


# this name looks good :)
class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = settings.WEBAUTHN.LOGIN_SERIALIZER

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        co = user.credential_options

        webuathn_user = WebAuthnUser(
            user_id=co.ukey,
            username=user.username,
            display_name=co.display_name,
            icon_url="",
            credential_id=co.credential_id,
            public_key=co.public_key,
            sign_count=co.sign_count,
            rp_id=settings.WEBAUTHN["RP_ID"],
        )

        webauthn_assertion_response = WebAuthnAssertionResponse(
            webuathn_user,
            request.data,
            co.challenge,
            settings.WEBAUTHN["ORIGIN"],
            uv_required=False,
        )

        try:
            sign_count = webauthn_assertion_response.verify()
        except AuthenticationRejectedException:
            return Response(
                {api_settings.NON_FIELD_ERRORS_KEY: "WebAuthn verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        co.sign_count = sign_count
        co.challenge = ""
        co.save()

        token_serializer_class = settings.SERIALIZERS.token
        token = login_user(request, user)
        return Response(
            token_serializer_class(token).data, status=status.HTTP_201_CREATED
        )
