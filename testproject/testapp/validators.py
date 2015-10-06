def is_666(value):
    from rest_framework import serializers
    if value == '666':
        raise serializers.ValidationError('Woops, 666 is not allowed.')
