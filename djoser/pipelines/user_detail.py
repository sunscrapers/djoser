from django.contrib.auth import get_user_model

from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def perform(request, context):
    assert hasattr(request, 'user')

    user = request.user
    return {'user': user}


def serialize_instance(request, context):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(context['user'])
    return {'response_data': serializer.data}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.user_detail
