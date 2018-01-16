from django.contrib.auth import get_user_model

from djoser import exceptions, utils
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    serializer_class = settings.SERIALIZERS.password_reset
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context

    email = context['serializer'].validated_data['email']
    users = utils.get_users_for_email(email)

    for user in users:
        user_email = utils.get_user_email(user)
        assert user_email is not None
        to = [user_email]
        settings.EMAIL.password_reset(request, {'user': user}).send(to)

    return {'users': users}


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.password_reset
