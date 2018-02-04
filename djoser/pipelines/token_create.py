from django.contrib.auth import get_user_model, user_logged_in

from djoser import constants, exceptions, signals
from djoser.conf import settings

User = get_user_model()


def serialize_request(request, **kwargs):
    serializer_class = settings.SERIALIZERS['token_create']
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(serializer, **kwargs):
    user = serializer.validated_data['user']
    if not settings.TOKEN_MODEL:
        raise exceptions.ValidationError(constants.TOKEN_MODEL_NONE_ERROR)

    token, _ = settings.TOKEN_MODEL.objects.get_or_create(user=user)
    return {'token': token, 'user': user}


def signal(request, user, **kwargs):
    signals.token_created.send(sender=None, user=user, request=request)
    user_logged_in.send(sender=None, user=user, request=request)


def serialize_instance(token, **kwargs):
    serializer_class = settings.SERIALIZERS['token']
    serializer = serializer_class(token)
    return {'response_data': serializer.data}
