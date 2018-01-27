from django.contrib.auth import get_user_model
from rest_framework.utils import model_meta

from djoser import exceptions, signals
from djoser.conf import settings

User = get_user_model()


def serialize_request(request, **kwargs):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, serializer, **kwargs):
    assert hasattr(request, 'user')

    # From rest_framework/serializers.py L946
    info = model_meta.get_field_info(request.user)
    for attr, value in serializer.validated_data.items():
        if attr in info.relations and info.relations[attr].to_many:
            field = getattr(request.user, attr)
            field.set(value)
        else:
            setattr(request.user, attr, value)
    request.user.save()

    return {'user': request.user}


def signal(request, user, **kwargs):
    signals.user_updated.send(sender=None, user=user, request=request)


def serialize_instance(user, **kwargs):
    serializer_class = settings.SERIALIZERS.user
    serializer = serializer_class(user)
    return {'response_data': serializer.data}
