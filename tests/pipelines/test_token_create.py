import pytest

from django.contrib.auth import get_user_model

from djoser import constants, exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {
        User.USERNAME_FIELD: getattr(test_user, User.USERNAME_FIELD),
        'password': 'testing123',
    }
    context = {'request': request}
    result = pipelines.token_create.serialize_request(**context)

    assert 'serializer' in result
    assert 'user' in result['serializer'].validated_data


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_invalid_credentials(test_user):
    request = mock.MagicMock()
    request.data = {
        User.USERNAME_FIELD: getattr(test_user, User.USERNAME_FIELD),
        'password': 'wrong-credentials',
    }
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_create.serialize_request(**context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_CREDENTIALS_ERROR]
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_empty_request(test_user):
    request = mock.MagicMock()
    request.data = {}
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_create.serialize_request(**context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_CREDENTIALS_ERROR]
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_user_not_active(inactive_test_user):
    request = mock.MagicMock()
    request.data = {
        User.USERNAME_FIELD: getattr(inactive_test_user, User.USERNAME_FIELD),
        'password': 'testing123',
    }
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_create.serialize_request(**context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_CREDENTIALS_ERROR]
    }


def test_valid_perform(test_user, settings):
    from djoser.conf import settings as djoser_settings

    settings.DJOSER = dict(
        settings.DJOSER,
        **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
    )

    serializer = mock.MagicMock()
    serializer.validated_data = {'user': test_user}
    context = {'serializer': serializer}

    result = pipelines.token_create.perform(**context)
    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1
    assert djoser_settings.TOKEN_MODEL.objects.first().user == test_user


@pytest.mark.django_db(transaction=False)
def test_invalid_perform_none_token_model(test_user):
    serializer = mock.MagicMock()
    serializer.validated_data = {'user': test_user}
    context = {'serializer': serializer}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_create.perform(**context)

    assert e.value.errors == constants.TOKEN_MODEL_NONE_ERROR


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.token_created) as handler:
        pipelines.token_create.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_created,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user, settings):
    from djoser.conf import settings as djoser_settings

    settings.DJOSER = dict(
        settings.DJOSER,
        **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
    )

    request = mock.MagicMock()
    request.data = {
        User.USERNAME_FIELD: getattr(test_user, User.USERNAME_FIELD),
        'password': 'testing123',
    }

    pipeline = pipelines.token_create.Pipeline(request)
    with catch_signal(signals.token_created) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_created,
        user=result['user'],
        request=request
    )

    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1
    assert djoser_settings.TOKEN_MODEL.objects.first().user == test_user
