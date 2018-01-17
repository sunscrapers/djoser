from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, **kwargs):
    serializer_class = settings.SERIALIZERS.user_delete
    context = {'request': request}
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, **kwargs):
    assert hasattr(request, 'user')

    user = request.user
    request.user.delete()
    return {'user': user}


def signal(request, user, **kwargs):
    signals.user_deleted.send(sender=None, user=user, request=request)


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_delete
