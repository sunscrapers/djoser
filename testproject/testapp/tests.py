from django.conf import settings
from django.contrib.auth import get_user_model, user_logged_in, user_login_failed, user_logged_out
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test.utils import override_settings
from djet import assertions, utils, restframework
from rest_framework import status
import djoser.views
import djoser.constants
import djoser.utils


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

        self.assert_status_equal(response, status.HTTP_200_OK)
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

        self.assert_status_equal(response, status.HTTP_200_OK)
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

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_emails_in_mailbox(0)


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

        self.assert_status_equal(response, status.HTTP_200_OK)
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


class ActivationViewTest(restframework.APIViewTestCase,
                         assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.ActivationView

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

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertTrue(user.is_active)


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

        self.assert_status_equal(response, status.HTTP_200_OK)
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

        self.assert_status_equal(response, status.HTTP_200_OK)
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
