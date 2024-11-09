import copy
import pickle
import re
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.test.utils import override_settings
from djoser.email import BaseDjoserEmail
from djoser.conf import settings as djoser_settings
import pytest


@pytest.mark.django_db
class TestDjoserEmail:
    @override_settings(DJOSER=dict())
    def test_base_djoser_email_get_context_data_with_no_settings_uses_defaults(self):
        base_djoser_email = BaseDjoserEmail()
        context_produced_without_settings = base_djoser_email.get_context_data()
        default_context = super(BaseDjoserEmail, base_djoser_email).get_context_data()
        default_context.pop("view")
        assert context_produced_without_settings == default_context

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{
                "EMAIL_FRONTEND_DOMAIN": "my_domain",
                "EMAIL_FRONTEND_SITE_NAME": "my_site_name",
                "EMAIL_FRONTEND_PROTOCOL": "https",
            },
        )
    )
    def test_base_djoser_email_get_context_data_overrides_defaults_correctly(self):
        base_djoser_email = BaseDjoserEmail()
        context_produced_using_settings = base_djoser_email.get_context_data()
        assert context_produced_using_settings.get("domain") == "my_domain"
        assert context_produced_using_settings.get("site_name") == "my_site_name"
        assert context_produced_using_settings.get("protocol") == "https"

    @override_settings(
        DJOSER=dict(
            settings.DJOSER,
            **{
                "EMAIL_FRONTEND_DOMAIN": "my_domain",
                "EMAIL_FRONTEND_SITE_NAME": "my_site_name",
                "EMAIL_FRONTEND_PROTOCOL": "https",
            },
        )
    )
    def test_all_emails_can_be_pickled(self, user):
        email_cls_keys = list(djoser_settings.EMAIL.keys())
        request = mock.MagicMock()
        for email_cls_key in email_cls_keys:
            email_class = getattr(djoser_settings.EMAIL, email_cls_key)
            email = email_class(request=request, context={"user": user})
            # not raises
            ctx = email.get_context_data()
            copy.deepcopy(ctx)
            pickle.dumps(ctx)


@pytest.mark.django_db
class TestEmailRender:
    @pytest.fixture
    @patch("templated_mail.mail.get_current_site")
    def mail_kwargs(self, get_current_site, user):
        site = mock.MagicMock()
        site.id = 1
        site.name = "Example"
        site.domain = "example.com"
        get_current_site.return_value = site
        request = mock.MagicMock()
        request.get_host.return_value = "my_host"

        return {"request": request, "context": {"user": user}}

    def test_activation(self, mail_kwargs):
        email_class = djoser_settings.EMAIL.activation
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""You're receiving this email because you need to finish activation process on my_host\.

Please go to the following page to activate account:
https:\/\/my_host\/#\/activate\/.*

Thanks for using our site!

The my_host team"""  # noqa: E501
        assert re.match(pattern, email.body, re.DOTALL) is not None

    def test_confirmation(self, mail_kwargs):
        email_class = djoser_settings.EMAIL.confirmation
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""Your account has been created and is ready to use!

Thanks for using our site!

The my_host team"""
        assert re.match(pattern, email.body, re.DOTALL) is not None

    def test_password_reset(self, mail_kwargs, user):
        email_class = djoser_settings.EMAIL.password_reset
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""You're receiving this email because you requested a password reset for your user account at my_host.

Please go to the following page and choose a new password:
https:\/\/my_host\/#\/password\/.*
Your username, in case you've forgotten: {username}

Thanks for using our site!

The my_host team""".format(  # noqa: E501
            username=user.username
        )
        assert re.match(pattern, email.body, re.DOTALL) is not None

    def test_password_changed_confirmation(self, mail_kwargs):
        email_class = djoser_settings.EMAIL.password_changed_confirmation
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""Your password has been changed!

Thanks for using our site!

The my_host team"""
        assert re.match(pattern, email.body, re.DOTALL) is not None

    def test_username_changed_confirmation(self, mail_kwargs):
        email_class = djoser_settings.EMAIL.username_changed_confirmation
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""Your username has been changed!

Thanks for using our site!

The my_host team"""
        assert re.match(pattern, email.body, re.DOTALL) is not None

    def test_username_reset(self, mail_kwargs, user):
        email_class = djoser_settings.EMAIL.username_reset
        email = email_class(**mail_kwargs)
        email.render()

        pattern = r"""You're receiving this email because you requested a username reset for your user account at my_host.

Please go to the following page and choose a new username:
https:\/\/my_host\/#\/username\/reset\/confirm\/.*
Your username, in case you've forgotten: {username}

Thanks for using our site!

The my_host team""".format(  # noqa: E501
            username=user.username
        )
        assert re.match(pattern, email.body, re.DOTALL) is not None
