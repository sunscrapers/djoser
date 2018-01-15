import pytest

from djoser import pipelines


def test_valid_activation_email_without_request(test_user, mailoutbox):
    context = {'user': test_user}
    assert test_user.is_active is True

    pipelines.email.activation_email(request=None, context=context)
    test_user.refresh_from_db()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert test_user.is_active is False


def test_failed_activation_email_user_without_email(test_user, mailoutbox):
    test_user.email = ''
    context = {'user': test_user}
    pipelines.email.activation_email(request=None, context=context)
    assert len(mailoutbox) == 0


def test_failed_activation_email_user_empty_context():
    context = {}
    with pytest.raises(AssertionError):
        pipelines.email.activation_email(request=None, context=context)


def test_valid_confirmation_email_without_request(test_user, mailoutbox):
    context = {'user': test_user}
    assert test_user.is_active is True

    pipelines.email.confirmation_email(request=None, context=context)
    test_user.refresh_from_db()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert test_user.is_active is True


def test_failed_confirmation_email_user_without_email(test_user, mailoutbox):
    test_user.email = ''
    context = {'user': test_user}
    pipelines.email.confirmation_email(request=None, context=context)
    assert len(mailoutbox) == 0


def test_failed_confirmation_email_user_empty_context():
    context = {}
    with pytest.raises(AssertionError):
        pipelines.email.confirmation_email(request=None, context=context)


def test_valid_password_reset_email_without_request(test_user, mailoutbox):
    context = {'user': test_user}
    assert test_user.is_active is True

    pipelines.email.password_reset_email(request=None, context=context)
    test_user.refresh_from_db()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [test_user.email]
    assert test_user.is_active is True


def test_failed_password_reset_email_user_without_email(test_user, mailoutbox):
    test_user.email = ''
    context = {'user': test_user}
    pipelines.email.password_reset_email(request=None, context=context)
    assert len(mailoutbox) == 0


def test_failed_password_reset_email_user_empty_context():
    context = {}
    with pytest.raises(AssertionError):
        pipelines.email.password_reset_email(request=None, context=context)
