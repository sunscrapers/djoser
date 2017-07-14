from djet import assertions, restframework
from rest_framework import status
import djoser.constants
import djoser.utils
import djoser.views


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
