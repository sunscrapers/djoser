from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings

User = get_user_model()


def serialize_request(request, **kwargs):
    if settings.PASSWORD_UPDATE_REQUIRE_RETYPE:
        serializer_class = settings.SERIALIZERS.set_password_retype
    else:
        serializer_class = settings.SERIALIZERS.set_password
    context = {'request': request}
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, serializer, **kwargs):
    new_password = serializer.validated_data['new_password']
    request.user.set_password(new_password)
    request.user.save()
    return {'user': request.user}


def signal(request, user, **kwargs):
    signals.password_updated.send(sender=None, user=user, request=request)
