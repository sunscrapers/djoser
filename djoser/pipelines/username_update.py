from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings

User = get_user_model()


def serialize_request(request, **kwargs):
    if settings.USERNAME_UPDATE_REQUIRE_RETYPE:
        serializer_class = settings.SERIALIZERS.set_username_retype
    else:
        serializer_class = settings.SERIALIZERS.set_username
    context = {'request': request}
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, serializer, **kwargs):
    user = request.user
    new_username = serializer.validated_data[User.USERNAME_FIELD]
    setattr(user, User.USERNAME_FIELD, new_username)
    user.save(update_fields=[User.USERNAME_FIELD])

    return {'user': user}


def signal(request, user, **kwargs):
    signals.username_updated.send(sender=None, user=user, request=request)
