import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse

User = get_user_model()


@pytest.mark.django_db
class TestUserPatchView:
    def test_patch_user_send_activation_email_when_inactive(
        self, user, authenticated_client, djoser_settings, mailoutbox
    ):
        # Enable activation email sending
        djoser_settings["SEND_ACTIVATION_EMAIL"] = True

        # Use correct URL pattern from reverse
        url = reverse("user-detail", kwargs={User._meta.pk.name: user.pk})
        data = {"email": "newemail@example.com"}

        response = authenticated_client.patch(url, data=data, format="json")

        # Verify the response
        assert response.status_code == status.HTTP_200_OK

        # Verify user became inactive
        user.refresh_from_db()
        assert not user.is_active
        assert user.email == "newemail@example.com"

        # Verify activation email was sent (lines 35-37)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == ["newemail@example.com"]

    def test_patch_user_no_email_when_activation_disabled(
        self, user, authenticated_client, djoser_settings, mailoutbox
    ):
        """
        Test that no email is sent when SEND_ACTIVATION_EMAIL is False.
        """

        # Disable activation email sending
        djoser_settings["SEND_ACTIVATION_EMAIL"] = False

        url = reverse("user-detail", kwargs={User._meta.pk.name: user.pk})
        data = {"email": "newemail@example.com"}

        response = authenticated_client.patch(url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # User should still be active since SEND_ACTIVATION_EMAIL is False
        user.refresh_from_db()
        assert user.is_active
        assert user.email == "newemail@example.com"

        # No email should be sent
        assert len(mailoutbox) == 0
