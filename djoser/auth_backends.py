from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from djoser.conf import settings


UserModel = get_user_model()


class LoginFieldBackend(ModelBackend):
    """Allows to log in by a different value than the default Django
    USERNAME_FIELD."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        get_kwargs = {
            settings.LOGIN_FIELD: username,
        }
        try:
            user = UserModel._default_manager.get(**get_kwargs)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
