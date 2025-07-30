import pytest
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.test import APIRequestFactory

from djoser.views.me.base import BaseMeAPIView

User = get_user_model()


@pytest.mark.django_db
class TestBaseMeAPIView:
    def test_get_queryset_with_custom_queryset(self, user):
        view = BaseMeAPIView()
        view.queryset = User  # Set custom queryset

        factory = APIRequestFactory()
        request = factory.get("/me/")
        request.user = user
        view.request = request

        queryset = view.get_queryset()

        # Should return filtered queryset for current user
        assert hasattr(queryset, "filter")
        # Convert to list to evaluate the queryset
        result_list = list(queryset)
        assert len(result_list) == 1
        assert result_list[0] == user

    def test_get_object_hide_users_unauthenticated(self, djoser_settings):
        view = BaseMeAPIView()

        factory = APIRequestFactory()
        request = factory.get("/me/")

        # Create an unauthenticated user
        unauthenticated_user = Mock()
        unauthenticated_user.is_authenticated = False
        request.user = unauthenticated_user
        view.request = request

        djoser_settings["HIDE_USERS"] = True
        with pytest.raises(NotFound):
            view.get_object()

    def test_permission_denied_hide_users_authenticated(self, user, djoser_settings):
        view = BaseMeAPIView()

        factory = APIRequestFactory()
        request = factory.get("/me/")
        request.user = user  # authenticated user

        djoser_settings["HIDE_USERS"] = True
        with pytest.raises(NotFound):
            view.permission_denied(request, message="Test message", code="test_code")

    def test_permission_denied_hide_users_false(self, user, djoser_settings):
        """
        Test that super().permission_denied is called when HIDE_USERS=False.
        """
        view = BaseMeAPIView()

        factory = APIRequestFactory()
        request = factory.get("/me/")
        request.user = user

        djoser_settings["HIDE_USERS"] = False
        with patch.object(
            view.__class__.__bases__[0], "permission_denied"
        ) as mock_super:
            view.permission_denied(request, message="Test message", code="test_code")
            mock_super.assert_called_once_with(request, "Test message", "test_code")

    def test_get_object_normal_case(self, user, djoser_settings):
        """
        Test get_object normal case when HIDE_USERS=False.
        """
        view = BaseMeAPIView()

        factory = APIRequestFactory()
        request = factory.get("/me/")
        request.user = user
        view.request = request

        djoser_settings["HIDE_USERS"] = False
        result = view.get_object()
        assert result == user

    def test_get_object_hide_users_authenticated(self, user, djoser_settings):
        """
        Test get_object when HIDE_USERS=True but user is authenticated (should work)
        """
        view = BaseMeAPIView()

        factory = APIRequestFactory()
        request = factory.get("/me/")
        request.user = user  # authenticated user
        view.request = request

        djoser_settings["HIDE_USERS"] = True
        result = view.get_object()
        assert result == user  # Should return user since they're authenticated
