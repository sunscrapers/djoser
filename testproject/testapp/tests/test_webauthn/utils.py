from testapp.factories import UserFactory
from djoser.webauthn.models import CredentialOptions


# WebAuthn test constants moved from individual test files
WEBAUTHN_TEST_DATA = {
    "REGISTRATION_CHALLENGE": "BG7Th4n4iNUmNuRqMjI8NUhFgcNPWmqP",
    "RP_NAME": "Web Authentication",
    "RP_ID": "3fadfd13.example.com",
    "ORIGIN": "https://3fadfd13.example.com",
    "USERNAME": "testuser",
    "USER_DISPLAY_NAME": "A Test User",
    "USER_ID": "\x80\xf1\xdc\xec\xb5\x18\xb1\xc8b\x05\x886\xbc\xdfJ\xdf",
    "CLIENT_DATA": (
        "ew0KCSJ0eXBlIiA6ICJ3ZWJhdXRobi5jcmVhdGUiLA0KCSJjaGFsbGVuZ2UiIDogIkJHN1RoNG40"
        "aU5VbU51UnFNakk4TlVoRmdjTlBXbXFQIiwNCgkib3JpZ2luIiA6ICJodHRwczovLzNmYWRmZDEz"
        "Lm5ncm9rLmlvIiwNCgkidG9rZW5CaW5kaW5nIiA6IA0KCXsNCgkJInN0YXR1cyIgOiAic3VwcG9y"
        "dGVkIg0KCX0NCn0"
    ),
    "ATT_OBJ": (
        "o2NmbXRkbm9uZWhhdXRoRGF0YVkBZ8-CnWXgcASczJuZcxGxAUOJ7xA1fHeCSAxHxXqSqlMsRQAA"
        "AABgKLAXsdRMArSzr82vyWuyACCgTbLFqUdf_NegYeOYWcLCYBXlUddoptLz2eQO5DHa4qQBAwM5"
        "AQAgWQEAyo6eM5iARhHve7LwTvbhxT39qHviHjC1tzauY5BFnqAqYsj6m5Hl6NdyGQEDI-NLrm9k"
        "GKlxGLoDUZLoQlUVL0W2oltsLPYtgKLpAoEf6QfQx51j86NZiRClNERVKsQ-CtceQl_ic7zvK7HT"
        "MQQM_yWtaYjGo9t2IDPVgrkVnoSzuz_N-9ylCgjCm23-sllb6XhgvpXj44TDpiZFOhJDhYQksuqT"
        "jA1s08eXrPDwvc1Bcq5N8lJIc3eva07vecuZB53ywY0oZRWZ58aV035jjjPd-Kxp5JGi3H03Ervn"
        "HJCVxv64d-ngx7WvnqwsEvGVG3nauadeGzYWuGkgsxddeSFDAQABZ2F0dFN0bXSg"
    ),
}


def get_webauthn_signup_data(username=None, email=None):
    """
    Get standard WebAuthn signup data.
    """
    return {
        "clientData": WEBAUTHN_TEST_DATA["CLIENT_DATA"],
        "attObj": WEBAUTHN_TEST_DATA["ATT_OBJ"],
        "username": username or WEBAUTHN_TEST_DATA["USERNAME"],
        "email": email or "john.doe@example.com",
    }


def get_webauthn_settings():
    """
    Get standard WebAuthn settings for tests.
    """
    return {
        "RP_NAME": WEBAUTHN_TEST_DATA["RP_NAME"],
        "RP_ID": WEBAUTHN_TEST_DATA["RP_ID"],
        "ORIGIN": WEBAUTHN_TEST_DATA["ORIGIN"],
    }


def create_credential_options(
    challenge="f00",
    username="john",
    display_name="John Doe",
    ukey="d34db33",
    with_user=False,
):
    return CredentialOptions.objects.create(
        challenge=challenge,
        username=username,
        display_name=display_name,
        ukey=ukey,
        user=None if not with_user else UserFactory.create(username=username),
        credential_id="f00",
    )
