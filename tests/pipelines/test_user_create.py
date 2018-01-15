import pytest

from django.contrib.auth import authenticate, get_user_model

from djoser import exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request():
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}
    result = pipelines.user_create.serialize_request(request, {})

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

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_create.serialize_request(request, {})

    assert e.value.errors == {'password': ['Password 666 is not allowed.']}


@pytest.mark.django_db(transaction=False)
def test_failed_serialize_request_duplicate_username(test_user):
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_create.serialize_request(request, {})

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
    result = pipelines.user_create.perform(None, context)

    assert User.objects.count() == 1
    assert 'user' in result

    username = getattr(result['user'], User.USERNAME_FIELD)
    assert username == serializer.validated_data[User.USERNAME_FIELD]
    assert result['user'].is_active is True
    assert authenticate(**{
        User.USERNAME_FIELD: serializer.validated_data[User.USERNAME_FIELD],
        'password': serializer.validated_data['password'],
    }) == result['user']


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'user': test_user}

    with catch_signal(signals.user_created) as handler:
        pipelines.user_create.signal(request, context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_created,
        user=test_user,
        request=request
    )


def test_valid_serialize_instance(test_user):
    context = {'user': test_user}
    result = pipelines.user_create.serialize_instance(None, context)
    username = getattr(test_user, User.USERNAME_FIELD)

    assert 'response_data' in result
    assert result['response_data'] == {User.USERNAME_FIELD: username, 'id': 1}


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline():
    request = mock.MagicMock()
    request.data = {User.USERNAME_FIELD: 'test', 'password': 'testing123'}

    pipeline = pipelines.user_create.Pipeline(request)
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
