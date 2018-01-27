from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings

User = get_user_model()


def serialize_request(request, **kwargs):
    serializer_class = settings.SERIALIZERS.user_activate
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(serializer, **kwargs):
    user = serializer.validated_data['user']
    user.is_active = True
    user.save(update_fields=['is_active'])

    return {'user': user}


def signal(request, user, **kwargs):
    signals.user_activated.send(sender=None, user=user, request=request)
