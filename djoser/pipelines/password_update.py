from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    if settings.SET_PASSWORD_RETYPE:
        serializer_class = settings.SERIALIZERS.set_password_retype
    else:
        serializer_class = settings.SERIALIZERS.set_password
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context

    new_password = context['serializer'].validated_data['new_password']
    request.user.set_password(new_password)
    request.user.save()
    return {'user': request.user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.password_updated.send(sender=None, user=user, request=request)


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.password_update
