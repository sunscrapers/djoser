from djet import restframework
from rest_framework.request import Request, override_method

import djoser.constants
import djoser.serializers
import djoser.signals
import djoser.utils
import djoser.views


class TestDjoserViewsSupportActionAttribute(restframework.APIViewTestCase):
    # any arbitrary view from djoser
    view_class = djoser.views.UserView

    def test_action_reflect_http_method(self):
        request = self.factory.get()

        view = self.view_class()
        view.action_map = {'get': 'retrieve'}

        # reproduce DRF wrapping
        with override_method(view, Request(request), 'GET') as request:
            view.dispatch(request)
            self.assertEqual(view.action, 'retrieve')
