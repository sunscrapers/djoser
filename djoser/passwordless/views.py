from djoser.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.constants import Messages
from djoser.compat import get_user_email
from djoser.views import TokenCreateView
from djoser import signals, utils

from .serializers import (
    EmailPasswordlessAuthSerializer,
    MobilePasswordlessAuthSerializer
)
from .services import PasswordlessTokenService

class AbstractPasswordlessTokenRequestView(APIView):
    """
    This returns a callback challenge token we can trade for a user's Auth Token.
    """
    success_response = Messages.TOKEN_SENT
    failure_response = Messages.CANNOT_SEND_TOKEN

    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @property
    def token_request_identifier(self):
        # "email" or "mobile"
        raise NotImplementedError

    def send(self, token):
        raise NotImplementedError

    def _respond_ok(self):
        status_code = status.HTTP_200_OK
        response_detail = self.success_response
        return Response({'detail': response_detail}, status=status_code)
        
    def _respond_not_ok(self):
        status_code = status.HTTP_400_BAD_REQUEST
        response_detail = self.failure_response
        return Response({'detail': response_detail}, status=status_code)


    def post(self, request, *args, **kwargs):
        if self.token_request_identifier.upper() not in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
            # Only allow auth types allowed in settings.
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            # Might create user if settings allow it, or return the user to whom the token should be sent.
            user = serializer.save()
            if not user:
                self._respond_not_ok()
                
            # Create and send callback token
            token = PasswordlessTokenService.create_token(user, self.token_request_identifier)
            self.send(token)
            
            if token:
                return self._respond_ok()
            else:
                return self._respond_not_ok()
        else:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class PasswordlessEmailTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.PASSWORDLESS.SERIALIZERS.passwordless_request_email_token
    token_request_identifier = 'email'

    def send(self, token):
        user = token.user
        context = {
            "user": user,
            "token": token.token,
            "short_token": token.short_token
          }
        to = [get_user_email(user)]
        settings.PASSWORDLESS.EMAIL.passwordless_request(self.request, context).send(to)


class PasswordlessMobileTokenRequestView(AbstractPasswordlessTokenRequestView):
    permission_classes = (AllowAny,)
    serializer_class = settings.PASSWORDLESS.SERIALIZERS.passwordless_request_mobile_token
    token_request_identifier = 'mobile'

    def send(self, token):
        return settings.PASSWORDLESS.SMS_SENDER(self.request, token)


class ExchangePasswordlessTokenForAuthTokenView(TokenCreateView):
    """Use this endpoint to obtain user authentication token."""

    serializer_class = settings.PASSWORDLESS.SERIALIZERS.passwordless_token_exchange
    permission_classes = settings.PASSWORDLESS.PERMISSIONS.passwordless_token_exchange

    def _action(self, serializer):
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )
        
        token = utils.login_user(self.request, user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )
    

