from django.contrib.auth import get_user_model
from rest_framework.utils import model_meta

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context
    assert hasattr(request, 'user')

    # From rest_framework/serializers.py L946
    info = model_meta.get_field_info(request.user)
    for attr, value in context['serializer'].validated_data.items():
        if attr in info.relations and info.relations[attr].to_many:
            field = getattr(request.user, attr)
            field.set(value)
        else:
            setattr(request.user, attr, value)
    request.user.save()

    return {'user': request.user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.user_updated.send(sender=None, user=user, request=request)


def serialize_instance(request, context):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(context['user'])
    return {'response_data': serializer.data}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_update
