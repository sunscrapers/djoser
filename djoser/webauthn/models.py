from django.conf import settings
from django.db import models


class CredentialOptions(models.Model):
    challenge = models.TextField()
    username = models.TextField(unique=True)
    display_name = models.TextField()
    ukey = models.TextField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="credential_options",
        null=True,
        on_delete=models.CASCADE,
    )
    credential_id = models.TextField()
    sign_count = models.IntegerField(null=True)
    public_key = models.TextField()
