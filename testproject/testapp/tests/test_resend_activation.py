import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser

from djoser.compat import get_user_email

User = get_user_model()


@pytest.fixture
def url():
    return reverse("user-resend-activation")


@pytest.fixture
def active_user(user):
    return user


@pytest.fixture
def inactive_user(user):
    user.is_active = False
    user.save()
    return user


@pytest.mark.django_db
class TestResendActivationEmail:
    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_resend_activation_view(self, client, url, inactive_user):
        data = {"email": inactive_user.email}
        response = client.post(url, data)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [inactive_user.email]
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": False}))
    def test_dont_resend_activation_when_disabled(self, client, url, inactive_user):
        data = {"email": inactive_user.email}
        response = client.post(url, data)

        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_dont_resend_activation_when_active(self, client, url, user):
        data = {"email": user.email}
        response = client.post(url, data)

        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_dont_resend_activation_when_no_password(self, client, url, inactive_user):
        inactive_user.set_unusable_password()
        inactive_user.save()
        data = {"email": inactive_user.email}
        response = client.post(url, data)

        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}),
    )
    def test_resend_activation_view_custom_user(
        self, client, url, mocker, inactive_user
    ):
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.views.User", CustomUser)

        data = {"custom_email": get_user_email(inactive_user)}
        response = client.post(url, data)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [get_user_email(inactive_user)]
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @override_settings(DJOSER=dict(settings.DJOSER, **{"SEND_ACTIVATION_EMAIL": True}))
    def test_post_should_return_no_content_if_user_does_not_exist(self, client, url):
        data = {"email": "john@beatles.com"}
        response = client.post(url, data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 0
