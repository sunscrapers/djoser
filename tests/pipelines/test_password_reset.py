import pytest

from django.contrib.auth import get_user_model

from djoser import email, exceptions, pipelines
from tests.common import mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {
        'email': test_user.email,
    }
    context = {'request': request}
    result = pipelines.password_reset.serialize_request(**context)

    assert 'serializer' in result


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request_email_does_not_exist():
    request = mock.MagicMock()
    request.data = {
        'email': 'lolwut_email@nopeland.com',
    }
    context = {'request': request}
    result = pipelines.password_reset.serialize_request(**context)

    assert 'serializer' in result


@pytest.mark.django_db(transaction=False)
def test_invalid_serialize_request_email_show_not_found(settings):
    settings.DJOSER = dict(
        settings.DJOSER, **{'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True}
    )
    request = mock.MagicMock()
    request.data = {
        'email': 'lolwut_email@nopeland.com',
    }
    context = {'request': request}
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset.serialize_request(**context)

    assert e.value.errors == {
        'email': ['User with given email does not exist.']
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user, mailoutbox):
    serializer = mock.MagicMock()
    serializer.validated_data = {
        'email': test_user.email,
    }

    context = {'request': None, 'serializer': serializer}
    result = pipelines.password_reset.perform(**context)

    assert 'users' in result
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert isinstance(mailoutbox[0], email.PasswordResetEmail)


@pytest.mark.django_db(transaction=False)
def test_valid_perform_email_does_not_exist(mailoutbox):
    serializer = mock.MagicMock()
    serializer.validated_data = {
        'email': 'lolwut_email@nopeland.com',
    }

    context = {'request': None, 'serializer': serializer}
    result = pipelines.password_reset.perform(**context)

    assert 'users' in result
    assert len(mailoutbox) == 0


@pytest.mark.django_db(transaction=False)
def test_valid_pipeline(test_user, mailoutbox):
    request = mock.MagicMock()
    request.data = {
        'email': test_user.email,
    }

    pipeline = pipelines.password_reset.Pipeline(request)
    result = pipeline.run()

    assert 'users' in result
    assert result['users'] == [test_user]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert isinstance(mailoutbox[0], email.PasswordResetEmail)
