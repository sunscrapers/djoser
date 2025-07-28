from testapp.factories import UserFactory
from djoser.webauthn.models import CredentialOptions


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
