import pytest
from testapp.factories import UserFactory
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from djoser.social.token.jwt import TokenStrategy


@pytest.mark.django_db
class TestJWTStrategy:
    def test_obtain_provides_valid_token_for_given_user(self):
        user = UserFactory.create()
        res = TokenStrategy.obtain(user)
        assert res["user"] == user

        data = {"token": res["access"]}
        serializer = TokenVerifySerializer(data=data)
        assert serializer.is_valid()
