import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from unittest import mock

from .utils import get_webauthn_signup_data, get_webauthn_settings, WEBAUTHN_TEST_DATA

User = get_user_model()


@pytest.mark.django_db
class TestSignupView:

    @pytest.fixture(autouse=True)
    def setup(self, djoser_settings):
        from djoser.webauthn.models import CredentialOptions

        djoser_settings.update(WEBAUTHN=get_webauthn_settings())

        self.url = reverse("webauthn_signup", args=[WEBAUTHN_TEST_DATA["USER_ID"]])
        self.co = CredentialOptions.objects.create(
            challenge=WEBAUTHN_TEST_DATA["REGISTRATION_CHALLENGE"],
            username=WEBAUTHN_TEST_DATA["USERNAME"],
            display_name=WEBAUTHN_TEST_DATA["USER_DISPLAY_NAME"],
            ukey=WEBAUTHN_TEST_DATA["USER_ID"],
            credential_id="f00",
        )

    @pytest.mark.parametrize("invalid_field", ["clientData", "attObj"])
    def test_post_with_invalid_registration_response_should_return_400(
        self, api_client, invalid_field
    ):
        data = get_webauthn_signup_data()
        data[invalid_field] = "invalid_data"
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_valid_registration_response_should_create_user(self, api_client):
        # Mock the WebAuthn verification to return a valid credential
        mock_credential = mock.Mock()
        mock_credential.credential_id.decode.return_value = "test_credential_id"
        mock_credential.public_key.decode.return_value = "test_public_key"
        mock_credential.sign_count = 0

        with mock.patch(
            "djoser.webauthn.views.WebAuthnRegistrationResponse"
        ) as mock_response_class:
            mock_response = mock_response_class.return_value
            mock_response.verify.return_value = mock_credential

            data = get_webauthn_signup_data()
            response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=WEBAUTHN_TEST_DATA["USERNAME"]).exists()

    def test_challenge_should_not_be_stored_after_successfull_signup(self, api_client):
        # Mock the WebAuthn verification to return a valid credential
        mock_credential = mock.Mock()
        mock_credential.credential_id.decode.return_value = "test_credential_id"
        mock_credential.public_key.decode.return_value = "test_public_key"
        mock_credential.sign_count = 0

        with mock.patch(
            "djoser.webauthn.views.WebAuthnRegistrationResponse"
        ) as mock_response_class:
            mock_response = mock_response_class.return_value
            mock_response.verify.return_value = mock_credential

            data = get_webauthn_signup_data()
            api_client.post(self.url, data=data)

        self.co.refresh_from_db()
        assert self.co.challenge == ""

    def test_register_user_when_email_confirmation_is_required(
        self, api_client, djoser_settings, mailoutbox
    ):
        djoser_settings.update(SEND_ACTIVATION_EMAIL=True)

        # Mock the WebAuthn verification to return a valid credential
        mock_credential = mock.Mock()
        mock_credential.credential_id.decode.return_value = "test_credential_id"
        mock_credential.public_key.decode.return_value = "test_public_key"
        mock_credential.sign_count = 0

        with mock.patch(
            "djoser.webauthn.views.WebAuthnRegistrationResponse"
        ) as mock_response_class:
            mock_response = mock_response_class.return_value
            mock_response.verify.return_value = mock_credential

            data = get_webauthn_signup_data()
            api_client.post(self.url, data=data)

        assert User.objects.filter(username=WEBAUTHN_TEST_DATA["USERNAME"]).exists()
        user = User.objects.get(username=WEBAUTHN_TEST_DATA["USERNAME"])
        assert not user.is_active
        assert len(mailoutbox) == 1

    def test_post_with_empty_client_data_should_return_400(self, api_client):
        """
        Test error handling for empty client data.
        """
        data = get_webauthn_signup_data()
        data["clientData"] = ""
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_empty_attestation_object_should_return_400(self, api_client):
        """
        Test error handling for empty attestation object.
        """
        data = get_webauthn_signup_data()
        data["attObj"] = ""
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_malformed_base64_client_data_should_return_400(self, api_client):
        """
        Test error handling for malformed base64 client data.
        """
        data = get_webauthn_signup_data()
        data["clientData"] = "not-valid-base64-data!!!"
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_malformed_base64_attestation_object_should_return_400(
        self, api_client
    ):
        """
        Test error handling for malformed base64 attestation object.
        """
        data = get_webauthn_signup_data()
        data["attObj"] = "not-valid-base64-data!!!"
        response = api_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_missing_required_fields_should_return_400(self, api_client):
        """
        Test error handling for missing required fields.
        """
        incomplete_data = {"username": WEBAUTHN_TEST_DATA["USERNAME"]}
        response = api_client.post(self.url, data=incomplete_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.exists()

    def test_post_with_invalid_user_id_should_return_404(self, api_client):
        """
        Test error handling for invalid user ID in URL.
        """
        invalid_url = reverse("webauthn_signup", args=["invalid-user-id"])
        data = get_webauthn_signup_data()
        response = api_client.post(invalid_url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not User.objects.exists()
