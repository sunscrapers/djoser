import typing

from djoser.webauthn.models import CredentialOptions


def create_credential_options(
    challenge="f00",
    username="john",
    display_name="John Doe",
    ukey="d34db33",
    with_user=False,
    user: typing.Optional = None,
):
    return CredentialOptions.objects.create(
        challenge=challenge,
        username=username,
        display_name=display_name,
        ukey=ukey,
        user=None if not with_user else user,
        credential_id="f00",
    )
