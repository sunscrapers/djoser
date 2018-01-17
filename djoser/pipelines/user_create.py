from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, **kwargs):
    serializer_class = settings.SERIALIZERS.user_create
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(serializer, **kwargs):
    try:
        username_field = User.USERNAME_FIELD
        username = serializer.validated_data[username_field]
        user = User.objects.get(**{username_field: username})
    except User.DoesNotExist:
        user = User.objects.create_user(**serializer.validated_data)

    return {'user': user}


def signal(request, user, **kwargs):
    signals.user_created.send(sender=None, user=user, request=request)


def serialize_instance(user, **kwargs):
    serializer_class = settings.SERIALIZERS.user_create
    serializer = serializer_class(user)
    return {'response_data': serializer.data}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_create
