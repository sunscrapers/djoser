from django.core.exceptions import ValidationError

def is_666(value):
    from rest_framework import serializers
    if value == '666':
        raise serializers.ValidationError('Woops, 666 is not allowed.')

class Is665(object):
    def validate(self, password):
        if password == '665':
            raise ValidationError("Password 665 is not allowed.")
