import pytest
from copy import deepcopy

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.conf import settings as djoser_settings

from .utils import create_credential_options

User = get_user_model()


ASSERTION_CHALLENGE = "brKlY5qXLLumGhaGbHlgvSTyFI4EHrvP"
RP_NAME = "Web Authentication"
RP_ID = "3fadfd13.ngrok.io"
ORIGIN = "https://3fadfd13.ngrok.io"
USERNAME = "testuser"
USER_DISPLAY_NAME = "A Test User"
USER_ID = "\x80\xf1\xdc\xec\xb5\x18\xb1\xc8b\x05\x886\xbc\xdfJ\xdf"
LOGIN_DATA = {
    "authData": "z4KdZeBwBJzMm5lzEbEBQ4nvEDV8d4JIDEfFepKqUywFAAAAAQ",
    "clientData": "ew0KCSJ0eXBlIiA6ICJ3ZWJhdXRobi5nZXQiLA0KCSJjaGFsbGVuZ2UiIDogImJyS2xZNXFYTEx1bUdoYUdiSGxndlNUeUZJNEVIcnZQIiwNCgkib3JpZ2luIiA6ICJodHRwczovLzNmYWRmZDEzLm5ncm9rLmlvIiwNCgkidG9rZW5CaW5kaW5nIiA6IA0KCXsNCgkJInN0YXR1cyIgOiAic3VwcG9ydGVkIg0KCX0NCn0",  # noqa
    "signature": "65d05b43495d4babc0388e6d530d7b0d676b0c29ddab4dce2445ebd053cc77ce43acc6d820c0d8491a0bae7beb98de8751d7497e07e061b7d26f4e490cd64b8bcd0628e1f50848d12b43f17493c9baf02bd4250a92c5d095d85faf7152a5132cd5f27c8223e61e683885021678a5156a955970d574926c52eec63b3bd25a205c4b51cb15c34c92ddd25b0ad370de96423e4b3edf5876963392f2ac889953f166669b96d16f894ef88e347484ab3cc81bc2814fbaf4b13dd1d483038bc4fb1354d564bc5aa944139ce6408e9078eddb6abef3a8ef4a77bcf74296ffd14c66223131d905f81cd149e1b8979c1bd87a036fca68f166e0644539b180d44f82fd7ed7",  # noqa
    "username": USERNAME,
}
PUBLIC_KEY = "pAEDAzkBACBZAQDKjp4zmIBGEe97svBO9uHFPf2oe-IeMLW3Nq5jkEWeoCpiyPqbkeXo13IZAQMj40uub2QYqXEYugNRkuhCVRUvRbaiW2ws9i2AoukCgR_pB9DHnWPzo1mJEKU0RFUqxD4K1x5CX-JzvO8rsdMxBAz_Ja1piMaj23YgM9WCuRWehLO7P8373KUKCMKbbf6yWVvpeGC-lePjhMOmJkU6EkOFhCSy6pOMDWzTx5es8PC9zUFyrk3yUkhzd69rTu95y5kHnfLBjShlFZnnxpXTfmOOM934rGnkkaLcfTcSu-cckJXG_rh36eDHta-erCwS8ZUbedq5p14bNha4aSCzF115IUMBAAE"  # noqa


@pytest.mark.django_db
class TestLoginView:

    @pytest.fixture(autouse=True)
    def credential_options(self, djoser_settings):
        djoser_settings.update(
            WEBAUTHN={"RP_NAME": RP_NAME, "RP_ID": RP_ID, "ORIGIN": ORIGIN}
        )
        self.url = reverse("webauthn_login")
        co = create_credential_options(
            challenge=ASSERTION_CHALLENGE,
            username=USERNAME,
            display_name=USER_DISPLAY_NAME,
            ukey=USER_ID,
            with_user=True,
        )
        co.public_key = PUBLIC_KEY
        co.sign_count = 0
        co.save()
        yield co

    @pytest.mark.parametrize("invalid_field", list(LOGIN_DATA.keys()))
    def test_post_with_invalid_login_response_should_return_400(
        self, api_client, invalid_field
    ):
        data = deepcopy(LOGIN_DATA)
        data[invalid_field] = "invalid_data"
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_with_valid_login_response_should_create_and_return_auth_token(
        self, api_client
    ):
        data = deepcopy(LOGIN_DATA)
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert djoser_settings.TOKEN_MODEL.objects.exists()
        assert "auth_token" in response.json()

    def test_challenge_should_not_be_stored_after_successful_login(
        self, credential_options, api_client
    ):
        data = deepcopy(LOGIN_DATA)
        api_client.post(self.url, data=data)

        credential_options.refresh_from_db()
        assert credential_options.challenge == ""
