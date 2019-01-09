import pytest

from django.contrib.auth import get_user_model

from djoser import constants, exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


def test_valid_perform(test_user, settings):
    from djoser.conf import settings as djoser_settings

    settings.DJOSER = dict(
        settings.DJOSER,
        **{'TOKEN_MODEL': 'rest_framework.authtoken.models.Token'}
    )

    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}

    djoser_settings.TOKEN_MODEL.objects.get_or_create(user=test_user)
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1

    result = pipelines.token_delete.perform(**context)
    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 0


@pytest.mark.django_db(transaction=False)
def test_invalid_perform_none_token_model(test_user):
    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}

    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.token_delete.perform(**context)

    assert e.value.errors == constants.TOKEN_MODEL_NONE_ERROR


def test_valid_signal(test_user):
    request = mock.MagicMock()
    context = {'request': request, 'user': test_user}

    with catch_signal(signals.token_deleted) as handler:
        pipelines.token_delete.signal(**context)

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_deleted,
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
    request.user = test_user

    djoser_settings.TOKEN_MODEL.objects.get_or_create(user=test_user)
    assert djoser_settings.TOKEN_MODEL.objects.count() == 1

    steps = djoser_settings.PIPELINES['token_delete']
    pipeline = pipelines.base.Pipeline(request, steps)
    with catch_signal(signals.token_deleted) as handler:
        result = pipeline.run()

    handler.assert_called_once_with(
        sender=mock.ANY,
        signal=signals.token_deleted,
        user=result['user'],
        request=request
    )

    assert result['user'] == test_user
    assert djoser_settings.TOKEN_MODEL.objects.count() == 0
