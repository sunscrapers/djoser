from django.db import models
from django.conf import settings
from django.utils.timezone import now, timedelta

class PasswordlessChallengeToken(models.Model):
    
    # We will deliver two tokens. One which is long and one which is short.
    # The short one needs to be redeemed with the same identifier that it was
    # sent to. This is a mitigation to brute force attacks, that might be able 
    # to break a short token.
    # The long token can be redeemed without any other information, as it is
    # significantly harder to brute force.

    token = models.TextField(unique=True)
    short_token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    uses = models.IntegerField(default=0)
    token_request_identifier = models.TextField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="djoser_passwordless_tokens",
        null=True,
        on_delete=models.CASCADE,
    )

    def redeem(self):
        self.uses += 1
        return self.save()
  
    def is_valid(self, token_lifetime_seconds, max_token_uses):
        if self.created_at + timedelta(seconds=token_lifetime_seconds) < now():
            return False
        if self.uses >= max_token_uses:
            return False
        return True