from django.contrib.auth import get_user_model
from django.test.testcases import SimpleTestCase
from djet import restframework
from rest_framework.request import Request, override_method

import djoser.constants
import djoser.serializers
import djoser.signals
import djoser.utils
import djoser.views


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

        factory = djoser.utils.UserEmailFactoryBase(**valid_data)
        self.assertIsNotNone(factory.get_context())


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
