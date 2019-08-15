import pytest
from djet import assertions, restframework
from rest_framework import status

import djoser.views

# @pytest.mark.skip
# class RootViewTest(restframework.APIViewTestCase,
#                    assertions.StatusCodeAssertionsMixin):
#     viewset = djoser.views.View
#     # view_class = djoser.views.RootView
#
#     def test_get_should_return_urls_map(self):
#         request = self.factory.get()
#         view_object = self.create_view_object(request)
#         response = view_object.dispatch(request)
#
#         self.assert_status_equal(response, status.HTTP_200_OK)
#         urlpattern_names = view_object.aggregate_djoser_urlpattern_names()
#         urls_map = view_object.get_urls_map(request, urlpattern_names, None)
#         self.assertEqual(urls_map, response.data)
#
#     def test_all_urlpattern_names_are_in_urls_map(self):
#         request = self.factory.get()
#         view_object = self.create_view_object(request)
#         response = view_object.dispatch(request)
#
#         self.assert_status_equal(response, status.HTTP_200_OK)
#         urlpattern_names = view_object.aggregate_djoser_urlpattern_names()
#         for urlpattern_name in urlpattern_names:
#             self.assertIn(urlpattern_name, response.data)
#
#     def test_non_existent_urlpattern_results_in_empty_string(self):
#         request = self.factory.get()
#         view_object = self.create_view_object(request)
#
#         urlpattern_names = ['non-existent-urlpattern']
#         urls_map = view_object.get_urls_map(request, urlpattern_names, None)
#         self.assertEqual(urls_map, {urlpattern_names[0]: ''})
