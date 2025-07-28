import pytest
from testapp.factories import UserFactory
from rest_framework import status
from rest_framework.reverse import reverse

from djoser.webauthn.models import CredentialOptions


@pytest.mark.django_db
def test_post_with_duplicate_username_should_fail(api_client):
    url = reverse("webauthn_signup_request")
    user = UserFactory.create()
    data = {"username": user.username, "display_name": user.username}
    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_post_should_create_credential_options(api_client):
    url = reverse("webauthn_signup_request")
    data = {"username": "john", "display_name": "John Doe"}
    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert CredentialOptions.objects.filter(username=data["username"]).exists()
