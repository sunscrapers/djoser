import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from djoser import constants, exceptions, pipelines, signals, utils
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(inactive_test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(inactive_test_user.pk),
        'token': default_token_generator.make_token(inactive_test_user)
    }
    result = pipelines.user_activate.serialize_request(request, {})

    assert 'serializer' in result
    assert 'user' in result['serializer'].validated_data
    assert result['serializer'].validated_data['user'] == inactive_test_user


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_wrong_uid():
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(1),
        'token': 'whatever',
    }
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_activate.serialize_request(request, {})

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_UID_ERROR]
    }


def test_invalid_serialize_request_stale_token(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk),
        'token': default_token_generator.make_token(test_user),
    }
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_activate.serialize_request(request, {})

    assert e.value.errors == {
        'non_field_errors': ['Stale token for given user.']
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(inactive_test_user):
    serializer = mock.MagicMock()
    serializer.validated_data = {'user': inactive_test_user}
    context = {'serializer': serializer}

    assert inactive_test_user.is_active is False
    result = pipelines.user_activate.perform(None, context)
    assert inactive_test_user.is_active is True
    assert result['user'] == inactive_test_user


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'user': test_user}

    with catch_signal(signals.user_activated) as handler:
        pipelines.user_activate.signal(request, context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_activated,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(inactive_test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(inactive_test_user.pk),
        'token': default_token_generator.make_token(inactive_test_user)
    }

    pipeline = pipelines.user_activate.Pipeline(request)
    with catch_signal(signals.user_activated) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_activated,
        user=result['user'],
        request=request
    )

    assert inactive_test_user.is_active is False
    inactive_test_user.refresh_from_db()
    assert inactive_test_user.is_active is True
