from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.test.utils import override_settings
from djet import assertions, restframework, utils
from rest_framework import status
import djoser.constants
import djoser.utils
import djoser.views

from .common import create_user


class PasswordResetConfirmViewTest(restframework.APIViewTestCase,
                                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.PasswordResetConfirmView

    def test_post_set_new_password(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
        }

        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user = utils.refresh(user)
        self.assertTrue(user.check_password(data['new_password']))

    def test_post_not_set_new_password_if_broken_uid(self):
        user = create_user()
        data = {
            'uid': 'x',
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uid', response.data)
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password']))

    def test_post_readable_error_message_when_uid_is_broken(self):
        """
        Regression test for https://github.com/sunscrapers/djoser/issues/122

        When uid was not correct unicode string, error message was a
        standard Python error messsage. Now we provide human readable message.
        """
        user = create_user()
        data = {
            'uid': b'\xd3\x10\xb4',
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uid', response.data)
        self.assertEqual(len(response.data['uid']), 1)
        self.assertEqual(
            response.data['uid'][0], djoser.constants.INVALID_UID_ERROR
        )

    def test_post_not_set_new_password_if_user_does_not_exist(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk + 1),
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uid', response.data)
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password']))

    def test_post_not_set_new_password_if_wrong_token(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': 'wrong-token',
            'new_password': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'],
            [djoser.constants.INVALID_TOKEN_ERROR]
        )
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password']))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True})
    )
    def test_post_not_set_new_password_if_password_mismatch(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
            're_new_password': 'wrong',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'],
            [djoser.constants.PASSWORD_MISMATCH_ERROR]
        )

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True})
    )
    def test_post_not_set_new_password_if_mismatch(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
            'new_password': 'new password',
            're_new_password': 'wrong',
        }

        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password']))

    @override_settings(
        DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True})
    )
    def test_post_not_reset_if_fails_password_validation(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
            'new_password': '666',
            're_new_password': 'isokpassword',
        }

        request = self.factory.post(data=data)
        response = self.view(request)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'new_password': ['Password 666 is not allowed.']}
        )
