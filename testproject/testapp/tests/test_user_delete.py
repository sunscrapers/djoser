from django.contrib.auth import get_user_model
from djet import assertions, restframework
from rest_framework import status

import djoser.constants
import djoser.utils
import djoser.views

from .common import create_user

User = get_user_model()


class UserDeleteViewTest(restframework.APIViewTestCase,
                         assertions.StatusCodeAssertionsMixin,
                         assertions.EmailAssertionsMixin,
                         assertions.InstanceAssertionsMixin):
    view_class = djoser.views.UserDeleteView

    def test_delete_user_if_logged_in(self):
        user = create_user()
        self.assert_instance_exists(User, username='john')
        data = {
            'current_password': 'secret',
        }
        request = self.factory.post(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(User, username='john')

    def test_not_delete_if_fails_password_validation(self):
        user = create_user()
        self.assert_instance_exists(User, username='john')
        data = {
            'current_password': 'incorrect',
        }

        request = self.factory.post(user=user, data=data)
        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'current_password': ['Invalid password.']}
        )
