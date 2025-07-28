import pytest
from copy import deepcopy
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

User = get_user_model()

REGISTRATION_CHALLENGE = "BG7Th4n4iNUmNuRqMjI8NUhFgcNPWmqP"
RP_NAME = "Web Authentication"
RP_ID = "3fadfd13.ngrok.io"
ORIGIN = "https://3fadfd13.ngrok.io"
USERNAME = "testuser"
USER_DISPLAY_NAME = "A Test User"
USER_ID = "\x80\xf1\xdc\xec\xb5\x18\xb1\xc8b\x05\x886\xbc\xdfJ\xdf"
SIGNUP_DATA = {
    "clientData": "ew0KCSJ0eXBlIiA6ICJ3ZWJhdXRobi5jcmVhdGUiLA0KCSJjaGFsbGVuZ2UiIDogIkJHN1RoNG40aU5VbU51UnFNakk4TlVoRmdjTlBXbXFQIiwNCgkib3JpZ2luIiA6ICJodHRwczovLzNmYWRmZDEzLm5ncm9rLmlvIiwNCgkidG9rZW5CaW5kaW5nIiA6IA0KCXsNCgkJInN0YXR1cyIgOiAic3VwcG9ydGVkIg0KCX0NCn0",  # noqa
    "attObj": "o2NmbXRkbm9uZWhhdXRoRGF0YVkBZ8-CnWXgcASczJuZcxGxAUOJ7xA1fHeCSAxHxXqSqlMsRQAAAABgKLAXsdRMArSzr82vyWuyACCgTbLFqUdf_NegYeOYWcLCYBXlUddoptLz2eQO5DHa4qQBAwM5AQAgWQEAyo6eM5iARhHve7LwTvbhxT39qHviHjC1tzauY5BFnqAqYsj6m5Hl6NdyGQEDI-NLrm9kGKlxGLoDUZLoQlUVL0W2oltsLPYtgKLpAoEf6QfQx51j86NZiRClNERVKsQ-CtceQl_ic7zvK7HTMQQM_yWtaYjGo9t2IDPVgrkVnoSzuz_N-9ylCgjCm23-sllb6XhgvpXj44TDpiZFOhJDhYQksuqTjA1s08eXrPDwvc1Bcq5N8lJIc3eva07vecuZB53ywY0oZRWZ58aV035jjjPd-Kxp5JGi3H03ErvnHJCVxv64d-ngx7WvnqwsEvGVG3nauadeGzYWuGkgsxddeSFDAQABZ2F0dFN0bXSg",  # noqa
    "username": USERNAME,
    "email": "john.doe@example.com",
}


@pytest.mark.django_db
class TestSignupView:

    @pytest.fixture(autouse=True)
    def setup(self, djoser_settings):
        from djoser.webauthn.models import CredentialOptions

        djoser_settings.update(
            WEBAUTHN={"RP_NAME": RP_NAME, "RP_ID": RP_ID, "ORIGIN": ORIGIN}
        )

        self.url = reverse("webauthn_signup", args=[USER_ID])
        self.co = CredentialOptions.objects.create(
            challenge=REGISTRATION_CHALLENGE,
            username=USERNAME,
            display_name=USER_DISPLAY_NAME,
            ukey=USER_ID,
            credential_id="f00",
        )

    @pytest.mark.parametrize("invalid_field", ["clientData", "attObj"])
    def test_post_with_invalid_registration_response_should_return_400(
        self, api_client, invalid_field
    ):
        data = deepcopy(SIGNUP_DATA)
        data[invalid_field] = "invalid_data"
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_valid_registration_response_should_create_user(self, api_client):
        data = deepcopy(SIGNUP_DATA)
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=USERNAME).exists()

    def test_challenge_should_not_be_stored_after_successfull_signup(self, api_client):
        data = deepcopy(SIGNUP_DATA)
        api_client.post(self.url, data=data)

        self.co.refresh_from_db()
        assert self.co.challenge == ""

    def test_register_user_when_email_confirmation_is_required(
        self, api_client, djoser_settings, mailoutbox
    ):
        djoser_settings.update(SEND_ACTIVATION_EMAIL=True)
        data = deepcopy(SIGNUP_DATA)
        api_client.post(self.url, data=data)

        assert User.objects.filter(username=USERNAME).exists()
        user = User.objects.get(username=USERNAME)
        assert not user.is_active
        assert len(mailoutbox) == 1
