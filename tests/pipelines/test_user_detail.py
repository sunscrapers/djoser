import pytest

from django.contrib.auth import get_user_model

from djoser import pipelines
from djoser.conf import settings
from tests.common import mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user):
    request = mock.MagicMock()
    request.user = test_user
    context = {'request': request}
    result = pipelines.user_detail.perform(**context)

    assert result['user'] == test_user


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_instance(test_user):
    context = {'user': test_user}
    result = pipelines.user_detail.serialize_instance(**context)
    username = getattr(test_user, User.USERNAME_FIELD)

    assert 'response_data' in result
    assert result['response_data'] == {
        'id': 1,
        'email': test_user.email,
        User.USERNAME_FIELD: username,
    }


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user):
    request = mock.MagicMock()
    request.user = test_user
    username = getattr(test_user, User.USERNAME_FIELD)

    steps = settings.PIPELINES.user_detail
    pipeline = pipelines.base.Pipeline(request, steps)
    result = pipeline.run()

    assert 'response_data' in result
    assert result['response_data'] == {
        'id': 1,
        'email': test_user.email,
        User.USERNAME_FIELD: username,
    }
