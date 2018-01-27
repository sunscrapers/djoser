from django.contrib.auth import get_user_model, user_logged_out

from djoser import constants, exceptions, signals
from djoser.conf import settings

User = get_user_model()


def perform(request, **kwargs):
    assert hasattr(request, 'user')

    if not settings.TOKEN_MODEL:
        raise exceptions.ValidationError(constants.TOKEN_MODEL_NONE_ERROR)

    settings.TOKEN_MODEL.objects.filter(user=request.user).delete()
    return {'user': request.user}


def signal(request, user, **kwargs):
    signals.token_destroyed.send(sender=None, user=user, request=request)
    user_logged_out.send(sender=None, user=user, request=request)
