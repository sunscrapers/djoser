import pytest

from django.contrib.auth import get_user_model

from djoser import exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {'current_password': 'testing123'}
    request.user = test_user
    context = {'request': request}
    result = pipelines.user_delete.serialize_request(**context)

    assert User.objects.count() == 1
    assert result['serializer'].context['request'].user == test_user


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_wrong_password(test_user):
    request = mock.MagicMock()
    request.data = {'current_password': 'lolwut'}
    request.user = test_user
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.user_delete.serialize_request(**context)

    assert e.value.errors == {'current_password': ['Invalid password.']}


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}
    result = pipelines.user_delete.perform(**context)

    assert User.objects.count() == 0
    assert 'user' in result
    assert result['user'].username == test_user.username
    assert result['user'].email == test_user.email


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.user_deleted) as handler:
        pipelines.user_delete.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_deleted,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user):
    request = mock.MagicMock()
    request.data = {'current_password': 'testing123'}
    request.user = test_user

    pipeline = pipelines.user_delete.Pipeline(request)
    with catch_signal(signals.user_deleted) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.user_deleted,
        user=result['user'],
        request=request
    )

    assert not User.objects.exists()
