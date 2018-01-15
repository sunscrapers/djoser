from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    serializer_class = settings.SERIALIZERS.user_create
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context

    try:
        username_field = User.USERNAME_FIELD
        username = context['serializer'].data[username_field]
        user = User.objects.get(**{username_field: username})
    except User.DoesNotExist:
        user = User.objects.create_user(
            **context['serializer'].validated_data
        )

    return {'user': user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.user_created.send(sender=None, user=user, request=request)


def serialize_instance(request, context):
    assert context['user']

    serializer_class = settings.SERIALIZERS.user_create
    serializer = serializer_class(context['user'])
    return {'response_data': serializer.data}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_create
