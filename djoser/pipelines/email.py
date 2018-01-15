from djoser import utils
from djoser.conf import settings


def activation_email(request, context):
    """
    Side effect of updating is_active field to False
    """
    utils.validate_context_user_for_email(context)
    user = context['user']

    user_email = utils.get_user_email(user)
    assert user_email is not None
    to = [user_email]
    settings.EMAIL.activation(request, context).send(to)

    user.is_active = False
    user.save(update_fields=['is_active'])


def confirmation_email(request, context):
    utils.validate_context_user_for_email(context)
    user = context['user']

    user_email = utils.get_user_email(user)
    assert user_email is not None
    to = [user_email]
    settings.EMAIL.confirmation(request, context).send(to)


def password_reset_email(request, context):
    utils.validate_context_user_for_email(context)
    user = context['user']

    user_email = utils.get_user_email(user)
    assert user_email is not None
    to = [user_email]
    settings.EMAIL.password_reset(request, context).send(to)
