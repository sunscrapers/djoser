from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    serializer_class = settings.SERIALIZERS.user_activate
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context
    assert 'user' in context['serializer'].validated_data

    user = context['serializer'].validated_data['user']
    user.is_active = True
    user.save(update_fields=['is_active'])

    return {'user': user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.user_activated.send(sender=None, user=user, request=request)


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_activate
