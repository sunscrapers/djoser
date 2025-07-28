import pytest
from testapp.factories import UserFactory, CustomUserFactory
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from unittest import mock

from testapp.models import CustomUser
from djoser.compat import get_user_email
from djoser.conf import settings as default_settings


@pytest.mark.django_db
def test_post_should_send_email_to_user_with_password_reset_link(
    api_client, mailoutbox
):
    base_url = reverse("user-reset-password")
    user = UserFactory.create()
    data = {"email": user.email}

    response = api_client.post(base_url, data)
    request = response.wsgi_request

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(mailoutbox) == 1
    assert user.email in [recipient for email in mailoutbox for recipient in email.to]
    site = get_current_site(request)
    assert site.domain in mail.outbox[0].body
    assert site.name in mail.outbox[0].body


@pytest.mark.django_db
def test_post_send_email_to_user_with_request_domain_and_site_name(api_client):
    base_url = reverse("user-reset-password")
    user = UserFactory.create()
    data = {"email": user.email}

    response = api_client.post(base_url, data)
    request = response.wsgi_request

    assert request.get_host() in mail.outbox[0].body


@pytest.mark.django_db
def test_post_should_not_send_email_to_user_if_user_does_not_exist(
    api_client, mailoutbox
):
    base_url = reverse("user-reset-password")
    data = {"email": "john@beatles.com"}

    response = api_client.post(base_url, data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(mailoutbox) == 0


@pytest.mark.django_db
def test_post_should_return_no_content_if_user_does_not_exist(api_client):
    base_url = reverse("user-reset-password")
    data = {"email": "john@beatles.com"}

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_post_should_return_bad_request_if_user_does_not_exist(
    api_client, djoser_settings
):
    djoser_settings.update(PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND=True)
    base_url = reverse("user-reset-password")
    data = {"email": "john@beatles.com"}

    response = api_client.post(base_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[0] == default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND


@pytest.mark.django_db
@mock.patch("djoser.serializers.User", CustomUser)
@mock.patch("djoser.views.User", CustomUser)
def test_post_should_send_email_to_custom_user_with_password_reset_link(
    api_client, djoser_settings, mailoutbox
):
    djoser_settings.update(AUTH_USER_MODEL="testapp.CustomUser")
    base_url = reverse("user-reset-password")
    user = CustomUserFactory.create(custom_required_field="42")
    data = {"custom_email": get_user_email(user)}

    response = api_client.post(base_url, data)
    request = response.wsgi_request

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(mailoutbox) == 1
    assert get_user_email(user) in [
        recipient for email in mailoutbox for recipient in email.to
    ]
    site = get_current_site(request)
    assert site.domain in mail.outbox[0].body
    assert site.name in mail.outbox[0].body


@pytest.mark.django_db
@mock.patch("djoser.serializers.User", CustomUser)
@mock.patch("djoser.views.User", CustomUser)
def test_post_should_return_bad_request_with_custom_email_field_if_user_does_not_exist(
    api_client, djoser_settings
):
    djoser_settings.update(
        AUTH_USER_MODEL="testapp.CustomUser", PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND=True
    )
    base_url = reverse("user-reset-password")
    data = {"custom_email": "john@beatles.com"}

    response = api_client.post(base_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[0] == default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND
