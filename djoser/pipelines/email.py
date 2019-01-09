from djoser import utils
from djoser.conf import settings


def activation_email(request, user, **kwargs):
    """
    Side effect of updating is_active field to False
    """
    user_email = utils.get_user_email(user)
    assert user_email is not None
    to = [user_email]
    context = {'user': user}
    context.update(kwargs)
    settings.EMAIL['activation'](request, context).send(to)

    user.is_active = False
    user.save(update_fields=['is_active'])


def confirmation_email(request, user, **kwargs):
    user_email = utils.get_user_email(user)
    assert user_email is not None
    to = [user_email]
    context = {'user': user}
    context.update(kwargs)
    settings.EMAIL['confirmation'](request, context).send(to)
