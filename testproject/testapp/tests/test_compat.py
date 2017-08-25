from django.contrib.auth import get_user_model
from django.test.testcases import SimpleTestCase
import django

from djoser.compat import get_user_email_field_name
from djoser.conf import settings

User = get_user_model()


class CompatTestCase(SimpleTestCase):
    def test_get_user_email_field_name_returns_proper_value(self):
        if django.VERSION >= (1, 11):
            email_field_name = User.get_email_field_name()
        else:
            email_field_name = settings.USER_EMAIL_FIELD_NAME

        user_email_field_name = get_user_email_field_name(User)
        self.assertEquals(user_email_field_name, email_field_name)
