import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from djoser import constants, exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@override_settings(DJOSER=dict(
    settings.DJOSER,
    **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
))
def test_valid_perform(test_user):
    from djoser.conf import settings as djoser_settings

    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}

    djoser_settings.TOKEN_MODEL.objects.get_or_create(user=test_user)
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1

    result = pipelines.token_destroy.perform(**context)
    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 0


@pytest.mark.django_db(transaction=False)
def test_invalid_perform_none_token_model(test_user):
    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_destroy.perform(**context)

    assert str(e.value) == constants.TOKEN_MODEL_NONE_ERROR


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.token_destroyed) as handler:
        pipelines.token_destroy.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_destroyed,
        user=test_user,
        request=request
    )


@pytest.mark.django_db(transaction=False)
@override_settings(DJOSER=dict(
    settings.DJOSER,
    **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
))
def test_valid_pipeline(test_user):
    from djoser.conf import settings as djoser_settings

    request = mock.MagicMock()
    request.user = test_user

    djoser_settings.TOKEN_MODEL.objects.get_or_create(user=test_user)
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1

    pipeline = pipelines.token_destroy.Pipeline(request)
    with catch_signal(signals.token_destroyed) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_destroyed,
        user=result['user'],
        request=request
    )

    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 0
