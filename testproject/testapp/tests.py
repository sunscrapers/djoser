from unittest import skipIf

import django
from django.conf import settings
from django.contrib.auth import get_user_model, user_logged_in, user_login_failed, user_logged_out
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test.utils import override_settings
from django.test.testcases import SimpleTestCase

from djet import assertions, utils, restframework

from rest_framework import status, authtoken
from rest_framework.request import Request, override_method

import djoser.views
import djoser.constants
import djoser.utils
import djoser.signals
import djoser.serializers

from djoser.settings import merge_settings_dicts

try:
    from unittest import mock
except ImportError:
    import mock


def create_user(**kwargs):
    data = {
        'username': 'john',
        'password': 'secret',
        'email': 'john@beatles.com',
    }
    data.update(kwargs)
    user = get_user_model().objects.create_user(**data)
    user.raw_password = data['password']
    return user


class RootViewTest(restframework.APIViewTestCase,
                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.RootView

    def test_get_should_return_urls_mapping(self):
        request = self.factory.get()
        view_object = self.create_view_object(request)

        response = view_object.dispatch(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        for key in view_object.get_urls_mapping().keys():
            self.assertIn(key, response.data)


class RegistrationViewTest(restframework.APIViewTestCase,
                           assertions.StatusCodeAssertionsMixin,
                           assertions.EmailAssertionsMixin,
                           assertions.InstanceAssertionsMixin):
    view_class = djoser.views.RegistrationView

    def test_post_should_create_user_without_login(self):
        data = {
            'username': 'john',
            'password': 'secret',
            'csrftoken': 'asdf',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue('password' not in response.data)
        self.assert_instance_exists(get_user_model(), username=data['username'])
        user = get_user_model().objects.get(username=data['username'])
        self.assertTrue(user.check_password(data['password']))

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True}))
    def test_post_should_create_user_with_login_and_send_activation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(get_user_model(), username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = get_user_model().objects.get(username='john')
        self.assertFalse(user.is_active)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SEND_CONFIRMATION_EMAIL': True}))
    def test_post_should_create_user_with_login_and_send_confirmation_email(self):
        data = {
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(get_user_model(), username=data['username'])
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = get_user_model().objects.get(username='john')
        self.assertTrue(user.is_active)

    def test_post_should_not_create_new_user_if_username_exists(self):
        create_user(username='john')
        data = {
            'username': 'john',
            'password': 'secret',
            'csrftoken': 'asdf',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_should_not_register_if_fails_password_validation(self):
        data = {
            'username': 'john',
            'password': '666',
            'csrftoken': 'asdf',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'password': ['Woops, 666 is not allowed.']})


class LoginViewTest(restframework.APIViewTestCase,
                    assertions.StatusCodeAssertionsMixin,
                    assertions.InstanceAssertionsMixin):
    view_class = djoser.views.LoginView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_login_user(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': user.raw_password,
        }
        user_logged_in.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(response.data['auth_token'], user.auth_token.key)
        self.assertTrue(self.signal_sent)

    @skipIf(django.VERSION >= (1, 10), "in this version authenticate() returns None if user is inactive")
    def test_post_should_not_login_if_user_is_not_active(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': user.raw_password,
        }
        user.is_active = False
        user.save()
        user_logged_in.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INACTIVE_ACCOUNT_ERROR])
        self.assertFalse(self.signal_sent)

    @skipIf(django.VERSION < (1, 10), "in these versions authenticate() succeedes if user is inactive")
    def test_post_should_not_login_if_user_is_not_active(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': user.raw_password,
        }
        user.is_active = False
        user.save()
        user_logged_in.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_CREDENTIALS_ERROR])
        self.assertFalse(self.signal_sent)

    def test_post_should_not_login_if_invalid_credentials(self):
        user = create_user()
        data = {
            'username': user.username,
            'password': 'wrong',
        }
        user_login_failed.connect(self.signal_receiver)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_CREDENTIALS_ERROR])
        self.assertTrue(self.signal_sent)

    def test_post_should_not_login_if_empty_request(self):
        data = {}
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_CREDENTIALS_ERROR])


class LogoutViewTest(restframework.APIViewTestCase,
                     assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.LogoutView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_logout_logged_in_user(self):
        user = create_user()
        user_logged_out.connect(self.signal_receiver)
        request = self.factory.post(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
        self.assertTrue(self.signal_sent)

    def test_post_should_deny_logging_out_when_user_not_logged_in(self):
        create_user()
        request = self.factory.post()

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_options(self):
        user = create_user()
        request = self.factory.options(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)


class PasswordResetViewTest(restframework.APIViewTestCase,
                            assertions.StatusCodeAssertionsMixin,
                            assertions.EmailAssertionsMixin):
    view_class = djoser.views.PasswordResetView

    def test_post_should_send_email_to_user_with_password_rest_link(self):
        user = create_user()
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])
        site = djoser.utils.get_current_site(request)
        self.assertIn(site.domain, mail.outbox[0].body)
        self.assertIn(site.name, mail.outbox[0].body)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'DOMAIN': 'custom.com', 'SITE_NAME': 'Custom'}))
    def test_post_should_send_email_to_user_with_custom_domain_and_site_name(self):
        user = create_user()
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        self.view(request)

        self.assertIn(settings.DJOSER['DOMAIN'], mail.outbox[0].body)
        self.assertIn(settings.DJOSER['SITE_NAME'], mail.outbox[0].body)

    def test_post_should_send_email_to_user_with_domain_and_site_name_from_request(self):
        user = create_user()
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        self.view(request)

        self.assertIn(request.get_host(), mail.outbox[0].body)

    def test_post_should_not_send_email_to_user_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(0)

    def test_post_should_return_no_content_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    @override_settings(
        DJOSER=dict(settings.DJOSER,
                    **{'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True}))
    def test_post_should_return_bad_request_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0],
                         djoser.constants.EMAIL_NOT_FOUND)


class PasswordResetConfirmViewTest(restframework.APIViewTestCase,
                                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.PasswordResetConfirmView

    def test_post_should_set_new_password(self):
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

    def test_post_should_not_set_new_password_if_broken_uid(self):
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
        """ Regression test for https://github.com/sunscrapers/djoser/issues/122

        When uid is not correct unicode string, error message was looked like:
        'utf-8' codec can't decode byte 0xd3 in position 0: invalid continuation byte.
        You passed in b'\xd3\x10\xb4' (<class 'bytes'>)

        Now we provide human readable message
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
        self.assertEqual(response.data['uid'][0], djoser.constants.INVALID_UID_ERROR)

    def test_post_should_not_set_new_password_if_user_does_not_exist(self):
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

    def test_post_should_not_set_new_password_if_wrong_token(self):
        user = create_user()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': 'wrong-token',
            'new_password': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_TOKEN_ERROR])
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password']))

    @override_settings(DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True}))
    def test_post_should_not_set_new_password_if_password_mismatch(self):
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
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.PASSWORD_MISMATCH_ERROR])

    @override_settings(DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True}))
    def test_post_should_not_set_new_password_if_mismatch(self):
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

    @override_settings(DJOSER=dict(settings.DJOSER, **{'PASSWORD_RESET_CONFIRM_RETYPE': True}))
    def test_post_should_not_reset_if_fails_password_validation(self):
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
        self.assertEqual(response.data, {'new_password': ['Woops, 666 is not allowed.']})


class ActivationViewTest(restframework.APIViewTestCase,
                         assertions.EmailAssertionsMixin,
                         assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.ActivationView

    def setUp(self):
        self.signal_sent = False

    def signal_receiver(self, *args, **kwargs):
        self.signal_sent = True

    def test_post_should_activate_user_and_not_login(self):
        user = create_user()
        user.is_active = False
        user.save()
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user = utils.refresh(user)
        self.assertTrue(user.is_active)

    def test_post_should_respond_with_bad_request_when_wrong_uid(self):
        data = {
            'uid': djoser.utils.encode_uid(1),
        }
        request = self.factory.post(data=data)

        response = self.view(request)
        response.render()

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_post_should_respond_with_bad_request_when_stale_token(self):
        user = create_user()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.signal_sent)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SEND_CONFIRMATION_EMAIL': True}))
    def test_post_should_sent_confirmation_email(self):
        user = create_user()
        user.is_active = False
        user.save()
        djoser.signals.user_activated.connect(self.signal_receiver)
        data = {
            'uid': djoser.utils.encode_uid(user.pk),
            'token': default_token_generator.make_token(user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])


class SetPasswordViewTest(restframework.APIViewTestCase,
                          assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetPasswordView

    def test_post_should_set_new_password(self):
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

    def test_post_should_not_set_new_password_if_wrong_current_password(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'wrong',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SET_PASSWORD_RETYPE': True}))
    def test_post_should_not_set_new_password_if_mismatch(self):
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

    def test_post_should_not_set_new_password_if_fails_password_validation(self):
        user = create_user()
        data = {
            'new_password': '666',
            're_new_password': '666',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'new_password': ['Woops, 666 is not allowed.']})

    @override_settings(DJOSER=dict(settings.DJOSER, **{'LOGOUT_ON_PASSWORD_CHANGE': True}))
    def test_post_should_logout_after_password_change(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)
        djoser.utils.login_user(request, user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = authtoken.models.Token.objects.filter(user=user).exists()
        self.assertFalse(is_logged)

    def test_post_should_not_logout_after_password_change_if_setting_is_false(self):
        user = create_user()
        data = {
            'new_password': 'new password',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)
        djoser.utils.login_user(request, user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        is_logged = authtoken.models.Token.objects.filter(user=user).exists()
        self.assertTrue(is_logged)


class SetUsernameViewTest(restframework.APIViewTestCase,
                          assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetUsernameView

    def test_post_should_set_new_username(self):
        user = create_user()
        data = {
            'new_username': 'ringo',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        user = utils.refresh(user)
        self.assertEqual(data['new_username'], user.username)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SET_USERNAME_RETYPE': True}))
    def test_post_should_not_set_new_username_if_mismatch(self):
        user = create_user()
        data = {
            'new_username': 'ringo',
            're_new_username': 'wrong',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(data['new_username'], user.username)

    def test_post_should_not_set_new_username_if_exists(self):
        username = 'tom'
        create_user(username=username)
        user = create_user(username='john')
        data = {
            'new_username': username,
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(user.username, username)

    def test_post_should_not_set_new_username_if_invalid(self):
        user = create_user()
        data = {
            'new_username': '$ wrong username #',
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        user = utils.refresh(user)
        self.assertNotEqual(user.username, data['new_username'])


class UserViewTest(restframework.APIViewTestCase,
                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.UserView

    def test_get_should_return_user(self):
        user = create_user()
        request = self.factory.get(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(
            [get_user_model().USERNAME_FIELD, get_user_model()._meta.pk.name] + get_user_model().REQUIRED_FIELDS
        ))

    def test_put_should_update_user(self):
        user = create_user()
        data = {
            'email': 'ringo@beatles.com',
        }
        request = self.factory.put(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertEqual(data['email'], user.email)


class UserEmailFactoryBaseTest(SimpleTestCase):
    def test_get_context_returns_data(self):
        valid_data = {
            'from_email': 'test@example.net',
            'user': get_user_model()(),
            'protocol': 'https',
            'domain': 'example.net',
            'site_name': 'example.net',
            'arbitrary_data': 'lorem ipsum'

        }

        factory = djoser.utils.UserEmailFactoryBase(
            **valid_data
        )

        self.assertIsNotNone(factory.get_context())


class SerializersManagerTest(SimpleTestCase):

    def test_serializer_manager_init(self):
        serializers_manager = djoser.serializers.SerializersManager({})
        self.assertFalse(serializers_manager.serializers)

    def test_get_serializer_non_proper_name(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer
        })
        self.assertRaises(Exception, serializers_manager.get, 'bad_name')

    def test_get(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer})
        serializer_class = serializers_manager.get('user')
        self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))

    def test_get_from_cache(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer})
        serializer_class = serializers_manager.get('user')
        self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))

        with mock.patch.object(
                djoser.serializers.SerializersManager, 'load_serializer') as load_serializer_mock:
            serializer_class = serializers_manager.get('user')
            self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))
            self.assertFalse(load_serializer_mock.called)


class TestMergeSettingsDict(SimpleTestCase):

    def test_merge_in_key(self):
        c = {1: {1: None}}
        d = {1: {2: None}}
        expected = {1: {1: None, 2: None}}
        self.assertEqual(merge_settings_dicts(c, d), expected)

    def test_merge_in_key_overwrite_sub_key(self):
        c = {1: {1: None}}
        d = {1: {2: None, 1: 'TEST'}}
        expected = {1: {1: 'TEST', 2: None}}
        self.assertEqual(merge_settings_dicts(c, d), expected)

    def test_merge_in_key_overwrite_sub_key_overwrite_conflicts_false(self):
        c = {1: {1: None}}
        d = {1: {2: None, 1: 'TEST'}}
        try:
            merge_settings_dicts(c, d, overwrite_conflicts=False)
            self.assertTrue(False)
        except Exception as error:
            self.assertEqual(str(error), 'Conflict at 1.1')


class TestDjoserViewsSupportActionAttribute(restframework.APIViewTestCase):
    # any arbitraty view from djoser
    view_class = djoser.views.UserView

    def test_action_reflect_http_method(self):
        request = self.factory.get()

        view = self.view_class()
        view.action_map = {'get': 'retrieve'}

        # reproduce DRF wrapping
        with override_method(view, Request(request), 'GET') as request:
            view.dispatch(request)
            self.assertEqual(view.action, 'retrieve')
