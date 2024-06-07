from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import ModelBackend
from django.db.models import Exists, OuterRef, Q
from djoser.conf import settings

User = get_user_model()


class LoginFieldBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(settings.LOGIN_FIELD)
        if username is None or password is None:
            return
        user = User.objects.filter(**kwargs).first()
        if user and not user.check_password(password):
            return
        if user and user.is_active:
            return user