import pytest

from djoser import pipelines


def test_valid_activation_email_without_request(test_user, mailoutbox):
    context = {'request': None, 'user': test_user}
    assert test_user.is_active is True

    pipelines.email.activation_email(**context)
    test_user.refresh_from_db()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert test_user.is_active is False


def test_failed_activation_email_user_without_email(test_user, mailoutbox):
    test_user.email = ''
    context = {'request': None, 'user': test_user}
    pipelines.email.activation_email(**context)
    assert len(mailoutbox) == 0


def test_failed_activation_email_context_missing_user():
    context = {'request': None}
    with pytest.raises(TypeError) as e:
        pipelines.email.activation_email(**context)

    assert "missing 1 required positional argument: 'user'" in str(e.value)


def test_failed_activation_email_context_missing_request():
    context = {'user': None}
    with pytest.raises(TypeError) as e:
        pipelines.email.activation_email(**context)

    assert "missing 1 required positional argument: 'request'" in str(e.value)


def test_valid_confirmation_email_without_request(test_user, mailoutbox):
    context = {'request': None, 'user': test_user}
    assert test_user.is_active is True

    pipelines.email.confirmation_email(**context)
    test_user.refresh_from_db()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert test_user.is_active is True


def test_failed_confirmation_email_user_without_email(test_user, mailoutbox):
    test_user.email = ''
    context = {'request': None, 'user': test_user}
    pipelines.email.confirmation_email(**context)
    assert len(mailoutbox) == 0


def test_failed_confirmation_email_context_missing_user():
    context = {'request': None}
    with pytest.raises(TypeError) as e:
        pipelines.email.confirmation_email(**context)

    assert "missing 1 required positional argument: 'user'" in str(e.value)


def test_failed_confirmation_email_context_missing_request():
    context = {'user': None}
    with pytest.raises(TypeError) as e:
        pipelines.email.confirmation_email(**context)

    assert "missing 1 required positional argument: 'request'" in str(e.value)