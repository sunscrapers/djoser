from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    if settings.PASSWORD_RESET_CONFIRM_REQUIRE_RETYPE:
        serializer_class = settings.SERIALIZERS.password_reset_confirm_retype
    else:
        serializer_class = settings.SERIALIZERS.password_reset_confirm
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context
    assert 'user' in context['serializer'].validated_data
    assert 'new_password' in context['serializer'].validated_data

    user = context['serializer'].validated_data['user']
    password = context['serializer'].validated_data['new_password']

    user.set_password(password)
    user.save()

    return {'user': user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.password_reset_completed.send(
        sender=None, user=user, request=request
    )


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.password_reset_confirm
