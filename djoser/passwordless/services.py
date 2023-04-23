
from django.utils.timezone import now, timedelta
from django.db.models import Q
from djoser.conf import settings
from django.db import transaction, IntegrityError
from .utils import (
    create_challenge,
)
from .models import PasswordlessChallengeToken

class PasswordlessTokenService(object):
    @staticmethod
    def create_token(user, identifier_type):
        # We need to ensure the token is unique, so we'll wrap it in a
        # transaction that retries if the token is not unique.
        tries = 0
        PasswordlessChallengeToken.objects.delete_expired(settings.PASSWORDLESS["TOKEN_LIFETIME"], settings.PASSWORDLESS["MAX_TOKEN_USES"])
        try:
            with transaction.atomic():
                return PasswordlessTokenService._generate_create_token(user, identifier_type)
        except IntegrityError as exception:
            if tries < 5:
                tries += 1
                return PasswordlessTokenService._generate_create_token(user, identifier_type)
            else:
                # If we've cannot generate a unique token after 5 tries, we'll
                # raise the exception. Maybe add a message to the admin to cleanup
                # expired stale tokens, or to increase the token length.
                raise exception

    @staticmethod
    def _generate_create_token(user, identifier_type):
        # Remove all tokens for this user when issuing a new one
        user.djoser_passwordless_tokens.all().delete()
        token = PasswordlessChallengeToken.objects.create(
            token = create_challenge(settings.PASSWORDLESS["LONG_TOKEN_LENGTH"], settings.PASSWORDLESS["LONG_TOKEN_CHARS"]),
            short_token = create_challenge(settings.PASSWORDLESS["SHORT_TOKEN_LENGTH"], settings.PASSWORDLESS["SHORT_TOKEN_CHARS"]),
            token_request_identifier=identifier_type,
            user=user
        )
        return token
    

    @staticmethod
    def check_token(challenge, identifier_field, identifier_value):
        if not challenge:
            return None
        try:
            token = PasswordlessChallengeToken.objects.get(
                Q(token=challenge) | Q(
                  **{
                    "short_token": challenge,
                    "token_request_identifier": identifier_field,
                    "user__"+identifier_field: identifier_value,
                  }
                )
            )
        except PasswordlessChallengeToken.DoesNotExist:
            return None

        if not token.is_valid(settings.PASSWORDLESS["TOKEN_LIFETIME"], settings.PASSWORDLESS["MAX_TOKEN_USES"]):
            return None
            
        token.redeem()
        return token
