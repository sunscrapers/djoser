import pytest
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from djoser.social.token.jwt import TokenStrategy


@pytest.mark.django_db
def test_jwt_strategy_obtain_provides_valid_token(user):
    res = TokenStrategy.obtain(user)
    assert res["user"] == user

    # Verify the access token
    assert "access" in res
    data = {"token": res["access"]}
    serializer = TokenVerifySerializer(data=data)
    assert serializer.is_valid()

    # Optionally verify the refresh token if needed
    assert "refresh" in res
    # Refresh token verification usually involves a separate endpoint/logic
