import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test.utils import override_settings

from djoser import constants, exceptions, pipelines, signals, utils
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk),
        'token': default_token_generator.make_token(test_user),
        'new_password': 'cool-new-password123',
    }
    context = {'request': request}
    result = pipelines.password_reset_confirm.serialize_request(
        request, context
    )
    validated_data = result['serializer'].validated_data

    assert 'serializer' in result
    assert 'user' in validated_data
    assert 'new_password' in validated_data
    assert validated_data['user'] == test_user
    assert validated_data['new_password'] == request.data['new_password']


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_wrong_uid():
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(1),
        'token': 'whatever',
        'new_password': 'whatever-again',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset_confirm.serialize_request(request, context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_UID_ERROR]
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_not_existent_user(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk + 1),
        'token': default_token_generator.make_token(test_user),
        'new_password': 'whatever-123',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset_confirm.serialize_request(request, context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_UID_ERROR]
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_invalid_token(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk),
        'token': 'invalid-token',
        'new_password': 'whatever-123',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset_confirm.serialize_request(request, context)

    assert e.value.errors == {
        'non_field_errors': [constants.INVALID_TOKEN_ERROR]
    }


@pytest.mark.django_db(transaction=False)
@override_settings(DJOSER=dict(
    settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_REQUIRE_RETYPE': True}
))
def test_invalid_serialize_request_password_retype_mismatch(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk),
        'token': default_token_generator.make_token(test_user),
        'new_password': 'whatever-123',
        're_new_password': 'meh',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset_confirm.serialize_request(request, context)

    assert e.value.errors == {
        'non_field_errors': [constants.PASSWORD_MISMATCH_ERROR]
    }


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_password_validation_fail(test_user):
    request = mock.MagicMock()
    request.data = {
        'uid': utils.encode_uid(test_user.pk),
        'token': default_token_generator.make_token(test_user),
        'new_password': '666',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset_confirm.serialize_request(request, context)

    assert e.value.errors == {
        'new_password': ['Password 666 is not allowed.']
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    serializer = mock.MagicMock()
    serializer.validated_data = {
        'user': test_user,
        'new_password': 'cool-new-password123',
    }
    context = {'serializer': serializer}
    result = pipelines.password_reset_confirm.perform(None, context)

    assert result['user'] == test_user
    assert test_user.check_password(serializer.validated_data['new_password'])


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'user': test_user}

    with catch_signal(signals.password_reset_completed) as handler:
        pipelines.password_reset_confirm.signal(request, context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.password_reset_completed,
        user=test_user,
        request=request
    )
