import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from djoser import exceptions, pipelines, signals
from djoser.conf import settings as djoser_settings
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {
        'current_password': 'testing123',
        'new_password': 'newpass123'
    }
    request.user = test_user
    context = {'request': request}
    result = pipelines.password_update.serialize_request(**context)

    assert 'serializer' in result


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_wrong_current_password(test_user):
    request = mock.MagicMock()
    request.data = {
        'current_password': 'wrong-password',
        'new_password': 'newpass123'
    }
    request.user = test_user
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_update.serialize_request(**context)

    assert e.value.errors == {
        'current_password': ['Invalid password.']
    }


@pytest.mark.django_db(transaction=False)
@override_settings(DJOSER=dict(settings.DJOSER, **{
    'SERIALIZERS': {
        'password_update':
            'djoser.serializers.PasswordUpdateRetypeSerializer'
    }
}))
def test_invalid_serialize_request_retype_mismatch(test_user):
    request = mock.MagicMock()
    request.data = {
        'current_password': 'testing123',
        'new_password': 'newpass123',
        're_new_password': 'wrong-password',
    }
    request.user = test_user
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_update.serialize_request(**context)

    assert e.value.errors == {
        'non_field_errors': ["The two password fields didn't match."]
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    request = mock.MagicMock()
    request.user = test_user
    serializer = mock.MagicMock()
    serializer.validated_data = {
        'current_password': 'testing123',
        'new_password': 'newpass123'
    }
    context = {'request': request, 'serializer': serializer}
    pipelines.password_update.perform(**context)

    assert test_user.check_password(serializer.validated_data['new_password'])


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.password_updated) as handler:
        pipelines.password_update.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.password_updated,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
@override_settings(DJOSER=dict(settings.DJOSER, **{
    'SERIALIZERS': {
        'password_update':
            'djoser.serializers.PasswordUpdateSerializer'
    }
}))
def test_valid_pipeline(test_user):
    request = mock.MagicMock()
    request.data = {
        'current_password': 'testing123',
        'new_password': 'newpass123'
    }
    request.user = test_user

    assert test_user.check_password(request.data['current_password'])
    steps = djoser_settings.PIPELINES['password_update']
    pipeline = pipelines.base.Pipeline(request, steps)
    with catch_signal(signals.password_updated) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.password_updated,
        user=result['user'],
        request=request
    )

    assert test_user.check_password(request.data['new_password'])
