from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from djet import testcases, assertions, utils
from rest_framework import status
import djoser.views
import djoser.constants


class RegistrationViewTest(testcases.ViewTestCase,
                           assertions.StatusCodeAssertionsMixin,
                           assertions.InstanceAssertionsMixin):
    view_class = djoser.views.RegistrationView

    def test_post_should_create_user(self):
        data = {
            'username': 'john',
            'password': 'secret',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(get_user_model(), username=data['username'])


class LoginViewTest(testcases.ViewTestCase,
                    assertions.StatusCodeAssertionsMixin,
                    assertions.InstanceAssertionsMixin):
    view_class = djoser.views.LoginView

    def test_post_should_login_user(self):
        data = {
            'username': 'john',
            'password': 'secret',
        }
        user = get_user_model().objects.create_user(**data)
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], user.auth_token.key)

    def test_post_should_not_login_if_user_is_not_active(self):
        data = {
            'username': 'john',
            'password': 'secret',
        }
        user = get_user_model().objects.create_user(**data)
        user.is_active = False
        user.save()
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.DISABLE_ACCOUNT_ERROR])

    def test_post_should_not_login_if_invalid_credentials(self):
        data = {
            'username': 'john',
            'password': 'wrong'
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_CREDENTIALS_ERROR])


class PasswordResetViewTest(testcases.ViewTestCase,
                            assertions.StatusCodeAssertionsMixin,
                            assertions.EmailAssertionsMixin):
    view_class = djoser.views.PasswordResetView

    def test_post_should_send_email_to_user_with_password_rest_link(self):
        user = get_user_model().objects.create_user(**{
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        })
        data = {
            'email': user.email,
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[user.email])

    def test_post_should_not_send_email_to_user_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_emails_in_mailbox(0)


class SetPasswordViewTest(testcases.ViewTestCase,
                          assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.SetPasswordView

    def test_post_should_set_new_password(self):
        user = get_user_model().objects.create_user(**{
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        })
        data = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'new_password1': 'new password',
            'new_password2': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertTrue(user.check_password(data['new_password1']))

    def test_post_should_not_set_new_password_if_broken_uid(self):
        user = get_user_model().objects.create_user(**{
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        })
        data = {
            'uid': 'x',
            'token': default_token_generator.make_token(user),
            'new_password1': 'new password',
            'new_password2': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uid', response.data)
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password1']))

    def test_post_should_not_set_new_password_if_user_does_not_exist(self):
        user = get_user_model().objects.create_user(**{
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        })
        data = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk + 1)),
            'token': default_token_generator.make_token(user),
            'new_password1': 'new password',
            'new_password2': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('uid', response.data)
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password1']))

    def test_post_should_not_set_new_password_if_wrong_token(self):
        user = get_user_model().objects.create_user(**{
            'username': 'john',
            'email': 'john@beatles.com',
            'password': 'secret',
        })
        data = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': 'wrong-token',
            'new_password1': 'new password',
            'new_password2': 'new password',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], [djoser.constants.INVALID_TOKEN_ERROR])
        user = utils.refresh(user)
        self.assertFalse(user.check_password(data['new_password1']))