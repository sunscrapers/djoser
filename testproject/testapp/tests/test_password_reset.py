import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from testapp.models import CustomUser

from djoser.compat import get_user_email
from djoser.conf import settings as default_settings

User = get_user_model()


@pytest.fixture
def url():
    return reverse("user-reset-password")


@pytest.mark.django_db
class TestPasswordResetView:
    def test_post_should_send_email_to_user_with_password_reset_link(
        self, anonymous_api_client, user, url
    ):
        data = {"email": user.email}
        response = anonymous_api_client.post(url, data)
        request = response.wsgi_request

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        site = get_current_site(request)
        assert site.domain in mail.outbox[0].body
        assert site.name in mail.outbox[0].body

    def test_post_send_email_to_user_with_request_domain_and_site_name(
        self, anonymous_api_client, user, url
    ):
        data = {"email": user.email}
        response = anonymous_api_client.post(url, data)
        request = response.wsgi_request
        assert len(mail.outbox) == 1
        assert request.get_host() in mail.outbox[0].body

    def test_post_should_not_send_email_to_user_if_user_does_not_exist(
        self, anonymous_api_client, url
    ):
        data = {"email": "john@beatles.com"}
        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 0

    def test_post_should_return_no_content_if_user_does_not_exist(
        self, anonymous_api_client, url
    ):
        data = {"email": "john@beatles.com"}
        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True})
    )
    def test_post_should_return_bad_request_if_user_does_not_exist(
        self, anonymous_api_client, url
    ):
        data = {"email": "john@beatles.com"}
        response = anonymous_api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()[0] == default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND

    @override_settings(AUTH_USER_MODEL="testapp.CustomUser")
    def test_post_should_send_email_to_custom_user_with_password_reset_link(
        self, anonymous_api_client, user, url, mocker
    ):
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.views.User", CustomUser)
        email_field_name = CustomUser.get_email_field_name()
        data = {email_field_name: get_user_email(user)}
        response = anonymous_api_client.post(url, data)
        request = response.wsgi_request

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [get_user_email(user)]
        site = get_current_site(request)
        assert site.domain in mail.outbox[0].body
        assert site.name in mail.outbox[0].body

    @override_settings(
        AUTH_USER_MODEL="testapp.CustomUser",
        DJOSER=dict(settings.DJOSER, **{"PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True}),
    )
    def test_post_should_return_bad_request_with_custom_email_field_if_user_does_not_exist(  # noqa: E501
        self, anonymous_api_client, mocker
    ):
        mocker.patch("djoser.serializers.User", CustomUser)
        mocker.patch("djoser.views.User", CustomUser)
        email_field_name = CustomUser.get_email_field_name()
        data = {email_field_name: "john@beatles.com"}
        custom_url = reverse("user-reset-password")

        response = anonymous_api_client.post(custom_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()[0] == default_settings.CONSTANTS.messages.EMAIL_NOT_FOUND
