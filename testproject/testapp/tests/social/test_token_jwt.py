from django.test import TestCase
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from djoser.social.token.jwt import TokenStrategy

from ..common import create_user


class JWTStrategyTestCase(TestCase):
    def test_obtain_provides_valid_token_for_given_user(self):
        user = create_user()
        res = TokenStrategy.obtain(user)
        self.assertEqual(res["user"], user)

        data = {"token": res["access"]}
        serializer = TokenVerifySerializer(data=data)
        self.assertTrue(serializer.is_valid())
