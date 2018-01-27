import pytest

from django.contrib.auth import authenticate, get_user_model

from djoser import constants, exceptions, pipelines, signals
from djoser.conf import settings
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request():
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}
    context = {'request': request}
    result = pipelines.user_create.serialize_request(**context)

    expected_data = {
        User.USERNAME_FIELD: request.data[User.USERNAME_FIELD],
        'password': request.data['password']
    }
    assert User.objects.count() == 0
    assert 'serializer' in result
    assert result['serializer'].validated_data == expected_data


@pytest.mark.django_db(transaction=False)
def test_failed_serialize_request_password_validation():
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': '666'}
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_create.serialize_request(**context)

    assert e.value.errors == {'password': ['Password 666 is not allowed.']}


@pytest.mark.django_db(transaction=False)
def test_failed_serialize_request_duplicate_username(test_user):
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_create.serialize_request(**context)

    assert e.value.errors == {
        'username': ['A user with that username already exists.']
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform():
    serializer = mock.MagicMock()
    serializer.validated_data = {
        User.USERNAME_FIELD: 'test',
        'password': 'testing123'
    }
    context = {'serializer': serializer}
    result = pipelines.user_create.perform(**context)

    assert User.objects.count() == 1
    assert 'user' in result

    username = getattr(result['user'], User.USERNAME_FIELD)
    assert username == serializer.validated_data[User.USERNAME_FIELD]
    assert result['user'].is_active is True
    assert authenticate(**{
        User.USERNAME_FIELD: serializer.validated_data[User.USERNAME_FIELD],
        'password': serializer.validated_data['password'],
    }) == result['user']


def test_failed_perform_user_already_exists(test_user):
    serializer = mock.MagicMock()
    serializer.validated_data = {
        User.USERNAME_FIELD: 'test',
        'password': 'testing123'
    }
    context = {'serializer': serializer}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_create.perform(**context)

    assert e.value.errors == constants.CANNOT_CREATE_USER_ERROR


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.user_created) as handler:
        pipelines.user_create.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_created,
        user=test_user,
        request=request
    )


def test_valid_serialize_instance(test_user):
    context = {'user': test_user}
    result = pipelines.user_create.serialize_instance(**context)
    username = getattr(test_user, User.USERNAME_FIELD)

    assert 'response_data' in result
    assert result['response_data'] == {User.USERNAME_FIELD: username, 'id': 1}


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline():
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}

    steps = settings.PIPELINES.user_create
    pipeline = pipelines.base.Pipeline(request, steps)
    with catch_signal(signals.user_created) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_created,
        user=result['user'],
        request=request
    )

    assert 'response_data' in result
    assert result['response_data'] == {
        User.USERNAME_FIELD: request.data[User.USERNAME_FIELD], 'id': 1
    }
