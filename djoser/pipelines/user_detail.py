from django.contrib.auth import get_user_model

from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def perform(request, **kwargs):
    assert hasattr(request, 'user')

    user = request.user
    return {'user': user}


def serialize_instance(user, **kwargs):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(user)
    return {'response_data': serializer.data}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_detail
