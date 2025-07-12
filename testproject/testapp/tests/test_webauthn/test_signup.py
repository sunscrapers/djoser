import pytest
from copy import deepcopy

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse

from .utils import create_credential_options

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


@pytest.fixture
def url():
    return reverse("webauthn_signup", args=[USER_ID])


@pytest.fixture
def credential_options(db):
    return create_credential_options(
        challenge=REGISTRATION_CHALLENGE,
        username=USERNAME,
        display_name=USER_DISPLAY_NAME,
        ukey=USER_ID,
        user=None,
    )


@pytest.mark.django_db
class TestSignupView:
    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.DJOSER = {
            **settings.DJOSER,
            **{"WEBAUTHN": {"RP_NAME": RP_NAME, "RP_ID": RP_ID, "ORIGIN": ORIGIN}},
        }
        return settings

    @pytest.mark.parametrize("invalid_field", ["clientData", "attObj"])
    def test_post_with_invalid_registration_response_should_return_400(
        self, anonymous_api_client, url, credential_options, invalid_field
    ):
        data = deepcopy(SIGNUP_DATA)
        data[invalid_field] = "invalid_data"
        response = anonymous_api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username=USERNAME).exists()

    def test_post_with_valid_registration_response_should_create_user(
        self, anonymous_api_client, url, credential_options
    ):
        data = deepcopy(SIGNUP_DATA)
        response = anonymous_api_client.post(url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=USERNAME).exists()

    def test_challenge_should_not_be_stored_after_successful_signup(
        self, anonymous_api_client, url, credential_options
    ):
        data = deepcopy(SIGNUP_DATA)
        anonymous_api_client.post(url, data=data)

        credential_options.refresh_from_db()
        assert credential_options.challenge == ""

    @override_settings(
        DJOSER=dict(django_settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True})
    )
    def test_register_user_when_email_confirmation_is_required(
        self, anonymous_api_client, url, credential_options
    ):
        data = deepcopy(SIGNUP_DATA)
        anonymous_api_client.post(url, data=data)

        assert User.objects.filter(username=USERNAME).exists()
        user = User.objects.get(username=USERNAME)
        assert not user.is_active
        assert len(mail.outbox) == 1
