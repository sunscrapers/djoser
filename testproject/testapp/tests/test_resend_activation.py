import pytest
from testapp.factories import UserFactory, CustomUserFactory
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser
from unittest import mock

from djoser.compat import get_user_email


@pytest.fixture
def base_url():
    return reverse("user-resend-activation")


def test_resend_activation_view(djoser_settings, client, base_url, mailoutbox):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    user = UserFactory.create(is_active=False)
    data = {"email": user.email}
    response = client.post(base_url, data)

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_dont_resend_activation_when_disabled(
    djoser_settings, client, base_url, mailoutbox
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = False
    user = UserFactory.create(is_active=False)
    data = {"email": user.email}
    response = client.post(base_url, data)

    assert len(mailoutbox) == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_dont_resend_activation_when_active(
    djoser_settings, client, base_url, mailoutbox
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    user = UserFactory.create(is_active=True)
    data = {"email": user.email}
    response = client.post(base_url, data)

    assert len(mailoutbox) == 0
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_dont_resend_activation_when_no_password(
    djoser_settings, client, base_url, mailoutbox
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    user = UserFactory.create(is_active=False)
    user.set_unusable_password()
    user.raw_password = None
    user.save()
    data = {"email": user.email}
    response = client.post(base_url, data)

    assert len(mailoutbox) == 0
    assert response.status_code == status.HTTP_204_NO_CONTENT


@mock.patch("djoser.serializers.User", CustomUser)
@mock.patch("djoser.views.User", CustomUser)
@pytest.mark.django_db(transaction=True)
def test_resend_activation_view_custom_user(
    djoser_settings, client, base_url, mailoutbox, settings
):
    settings.AUTH_USER_MODEL = "testapp.CustomUser"
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    user = CustomUserFactory.create(custom_required_field="42", is_active=False)
    data = {"custom_email": get_user_email(user)}
    response = client.post(base_url, data)

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [get_user_email(user)]
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_post_should_return_no_content_if_user_does_not_exist(
    djoser_settings, client, base_url
):
    djoser_settings["SEND_ACTIVATION_EMAIL"] = True
    data = {"email": "john@beatles.com"}

    response = client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT
