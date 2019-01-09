import pytest

from django.contrib.auth import get_user_model

from djoser import pipelines, signals
from djoser.conf import settings
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {'email': 'new@localhost'}
    context = {'request': request}
    result = pipelines.user_update.serialize_request(**context)

    assert 'serializer' in result
    assert result['serializer'].validated_data == request.data


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    request = mock.MagicMock()
    request.user = test_user
    old_email = test_user.email

    serializer = mock.MagicMock()
    serializer.validated_data = {'email': 'new@localhost'}
    context = {'request': request, 'serializer': serializer}
    result = pipelines.user_update.perform(**context)

    assert 'user' in result
    assert result['user'].username == test_user.username
    assert result['user'].email == serializer.validated_data['email']
    assert result['user'].email != old_email
    assert test_user.email == serializer.validated_data['email']


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.user_updated) as handler:
        pipelines.user_update.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_updated,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_instance(test_user):
    context = {'user': test_user}
    result = pipelines.user_update.serialize_instance(**context)
    username = getattr(test_user, User.USERNAME_FIELD)

    assert 'response_data' in result
    assert result['response_data'] == {
        'id': 1,
        'email': test_user.email,
        User.USERNAME_FIELD: username,
    }


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {'email': 'new@localhost'}
    username = getattr(test_user, User.USERNAME_FIELD)

    steps = settings.PIPELINES['user_update']
    pipeline = pipelines.base.Pipeline(request, steps)
    with catch_signal(signals.user_updated) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_updated,
        user=result['user'],
        request=request
    )

    assert test_user.email == request.data['email']
    assert 'response_data' in result
    assert result['response_data'] == {
        'id': 1,
        'email': test_user.email,
        User.USERNAME_FIELD: username,
    }


# TODO: test errors, test FK, test m2m
