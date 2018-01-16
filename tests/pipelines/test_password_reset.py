import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from djoser import email, exceptions, pipelines, signals
from tests.common import catch_signal, mock

User = get_user_model()


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request(test_user):
    request = mock.MagicMock()
    request.data = {
        'email': test_user.email,
    }
    result = pipelines.password_reset.serialize_request(request, {})

    assert 'serializer' in result


@pytest.mark.django_db(transaction=False)
def test_valid_serialize_request_email_does_not_exist():
    request = mock.MagicMock()
    request.data = {
        'email': 'lolwut_email@nopeland.com',
    }
    result = pipelines.password_reset.serialize_request(request, {})

    assert 'serializer' in result


@pytest.mark.django_db(transaction=False)
@override_settings(DJOSER=dict(
    settings.DJOSER, **{'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True}
))
def test_invalid_serialize_request_email_show_not_found():
    request = mock.MagicMock()
    request.data = {
        'email': 'lolwut_email@nopeland.com',
    }
    with pytest.raises(exceptions.ValidationError) as e:
        pipelines.password_reset.serialize_request(request, {})

    assert e.value.errors == {
        'email': ['User with given email does not exist.']
    }


@pytest.mark.django_db(transaction=False)
def test_valid_perform(test_user, mailoutbox):
    serializer = mock.MagicMock()
    serializer.validated_data = {
        'email': test_user.email,
    }

    context = {'serializer': serializer}
    result = pipelines.password_reset.perform(None, context)

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

    context = {'serializer': serializer}
    result = pipelines.password_reset.perform(None, context)

    assert 'users' in result
    assert len(mailoutbox) == 0
