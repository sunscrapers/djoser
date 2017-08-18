from django.conf import settings
from django.test.utils import override_settings
from djet import assertions, restframework, utils
from djoser.conf import settings as djoser_settings
from rest_framework import status
import djoser.utils
import djoser.views

from .common import create_user

Token = djoser_settings.TOKEN_MODEL


class SetPasswordViewTest(restframework.APIViewTestCase,
                          assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetPasswordView

    def test_post_set_new_password(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user = utils.refresh(user)
        self.assertTrue(user.check_password(data['new_password']))

    def test_post_not_set_new_password_if_wrong_current_password(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'wrong',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'SET_PASSWORD_RETYPE': True})
    )
    def test_post_not_set_new_password_if_mismatch(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            're_new_password': 'wrong',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertTrue(user.check_password(data['current_password']))

    def test_post_not_set_new_password_if_fails_validation(self):
        user = create_user()
        data = {
            'new_password': '666',
            're_new_password': '666',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'new_password': ['Password 666 is not allowed.']}
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'LOGOUT_ON_PASSWORD_CHANGE': True})
    )
    def test_post_logout_after_password_change(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)
        djoser.utils.login_user(request, user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = Token.objects.filter(user=user).exists()
        self.assertFalse(is_logged)

    def test_post_not_logout_after_password_change_if_setting_is_false(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)
        djoser.utils.login_user(request, user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = Token.objects.filter(user=user).exists()
        self.assertTrue(is_logged)
