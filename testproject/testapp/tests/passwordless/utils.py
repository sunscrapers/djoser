from testapp.tests.common import create_user
from djoser.passwordless.serializers import PasswordlessTokenService

def create_token(identifier_field):
    user = create_user()
    return PasswordlessTokenService.create_token(user, identifier_field)
