def is_666(value):
    from rest_framework import serializers
    if value == '666':
        raise serializers.ValidationError('Woops, 666 is not allowed.')


class DjangoTestValidator(object):
    def validate(self, value):
        from django.core import exceptions
        if value == '666':
            raise exceptions.ValidationError('Woops, 666 is not allowed.')
