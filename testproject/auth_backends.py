from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailAuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        ret = self._authenticate_by_email(**credentials)
        return ret

    def _authenticate_by_email(self, **credentials):
        User = get_user_model()

        email = credentials.get('email', credentials.get('username'))
        if email:
            user = User.objects.get(email=email)
            if user.check_password(credentials["password"]):
                return user
        return None
