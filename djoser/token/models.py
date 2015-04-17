import binascii
import os
from django.conf import settings
from django.db import models


class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='auth_tokens')
    client = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            'user',
            'client',
        )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return u'{0} (client: {1})'.format(self.key, self.client)

    LOGIN_FIELDS = (
        'client',
    )