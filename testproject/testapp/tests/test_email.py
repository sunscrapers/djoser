from django.conf import settings
from django.test.testcases import SimpleTestCase
from django.test.utils import override_settings
from djoser.email import BaseDjoserEmail


class BaseDjoserEmailTestCase(SimpleTestCase):
    @override_settings(DJOSER=dict())
    def test_base_djoser_email_get_context_data_with_no_settings_uses_defaults(self):
        base_djoser_email = BaseDjoserEmail()
        context_produced_without_settings = base_djoser_email.get_context_data()
        default_context = super(BaseDjoserEmail, base_djoser_email).get_context_data()
        self.assertEqual(context_produced_without_settings, default_context)

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
        self.assertEqual(context_produced_using_settings.get("domain"), "my_domain")
        self.assertEqual(
            context_produced_using_settings.get("site_name"), "my_site_name"
        )
        self.assertEqual(context_produced_using_settings.get("protocol"), "https")
