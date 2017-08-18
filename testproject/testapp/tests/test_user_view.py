from django.contrib.auth import get_user_model
from djet import assertions, restframework, utils
from rest_framework import status
import djoser.views

from .common import create_user

User = get_user_model()


class UserViewTest(restframework.APIViewTestCase,
                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.UserView

    def test_get_return_user(self):
        user = create_user()
        request = self.factory.get(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(
            [User.USERNAME_FIELD, User._meta.pk.name] + User.REQUIRED_FIELDS
        ))

    def test_put_update_user(self):
        user = create_user()
        data = {
            'email': 'ringo@beatles.com',
        }
        request = self.factory.put(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertEqual(data['email'], user.email)
