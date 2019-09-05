from djoser.webauthn.models import CredentialOptions
from testapp.tests.common import create_user


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
        user=None if not with_user else create_user(username=username),
        credential_id="f00",
    )
