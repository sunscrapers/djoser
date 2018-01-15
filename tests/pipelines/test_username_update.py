import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from djoser import exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {
        User.USERNAME_FIELD: 'new_username',
        'current_password': 'testing123',
    }
    context = {'request': request}
    result = pipelines.username_update.serialize_request(request, context)

    assert 'serializer' in result
    assert result['serializer'].validated_data == {
        User.USERNAME_FIELD: 'new_username',
        'current_password': 'testing123',
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_same_username(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {
        User.USERNAME_FIELD: getattr(test_user, User.USERNAME_FIELD),
        'current_password': 'testing123',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.username_update.serialize_request(request, context)

    assert e.value.errors == {
        'username': ['A user with that username already exists.']
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_invalid_username(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {
        User.USERNAME_FIELD: '$ lolwut #',
        'current_password': 'testing123',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.username_update.serialize_request(request, context)

    assert 'username' in e.value.errors
    assert len(e.value.errors['username']) == 1
    assert 'Enter a valid username.' in e.value.errors['username'][0]


@pytest.mark.django_db(transaction=False)
@override_settings(
    DJOSER=dict(settings.DJOSER, **{'SET_USERNAME_RETYPE': True})
)
def test_invalid_serialize_request_username_retype_mismatch(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {
        User.USERNAME_FIELD: 'new_username',
        're_' + User.USERNAME_FIELD: 'spanish_inquisition',
        'current_password': 'testing123',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.username_update.serialize_request(request, context)

    assert e.value.errors == {
        'non_field_errors': ["The two username fields didn't match."]
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    request = mock.MagicMock()
    request.user = test_user
    serializer = mock.MagicMock()
    serializer.validated_data = {
        User.USERNAME_FIELD: 'new_username',
        'current_password': 'testing123',
    }
    context = {'serializer': serializer}
    result = pipelines.username_update.perform(request, context)

    assert 'user' in result
    test_user.refresh_from_db()
    assert test_user == result['user']
    assert getattr(test_user, User.USERNAME_FIELD) == 'new_username'


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'user': test_user}

    with catch_signal(signals.username_updated) as handler:
        pipelines.username_update.signal(request, context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.username_updated,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user):
    request = mock.MagicMock()
    request.user = test_user
    request.data = {
        User.USERNAME_FIELD: 'new_username',
        'current_password': 'testing123',
    }

    pipeline = pipelines.username_update.Pipeline(request)
    with catch_signal(signals.username_updated) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.username_updated,
        user=result['user'],
        request=request
    )
