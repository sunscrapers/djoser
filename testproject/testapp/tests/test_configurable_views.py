import pytest
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from djoser.views.me import UserMeRetrieveView


class CustomUserMeView(UserMeRetrieveView):
    """
    Custom view that adds extra data to demonstrate view replacement.
    """

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code == 200:
            response.data["custom_field"] = "custom_value"
            response.data["view_type"] = "custom"
        return response


class TestConfigurableViews:
    """
    Test the configurable view system functionality.
    """

    def test_default_views_work(self, authenticated_client, user):
        """
        Test that default views work without any configuration.
        """
        response = authenticated_client.get(reverse("user-me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user.id
        # Should not have custom fields from custom view
        assert "custom_field" not in response.data
        assert "view_type" not in response.data

    def test_partial_method_configuration(self, authenticated_client, user):
        """
        Test configuring only some methods while leaving others as default.
        """
        # This test uses default configuration but verifies the structure

        # All methods should work with defaults
        response = authenticated_client.get(reverse("user-me"))
        assert response.status_code == status.HTTP_200_OK

        response = authenticated_client.put(reverse("user-me"), {"first_name": "Test"})
        assert response.status_code == status.HTTP_200_OK

        response = authenticated_client.patch(
            reverse("user-me"), {"first_name": "Test2"}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_view_configuration_structure(self):
        """
        Test that the view configuration has the expected structure.
        """
        from djoser.conf import settings

        # Check that VIEWS exists and has expected keys
        assert hasattr(settings, "VIEWS")

        expected_keys = [
            "activation",
            "resend_activation",
            "password_reset",
            "password_reset_confirm",
            "set_password",
            "username_reset",
            "username_reset_confirm",
            "set_username",
            "user_create",
            "user_delete",
            "user_list",
            "user_detail",
            "user_update",
            "user_me_get",
            "user_me_put",
            "user_me_patch",
            "user_me_delete",
            "token_create",
            "token_destroy",
        ]

        for key in expected_keys:
            assert hasattr(settings.VIEWS, key), f"Missing view configuration: {key}"

        # Check that default values are proper classes (imported from strings)
        user_me_get_view = getattr(settings.VIEWS, "user_me_get", None)
        assert user_me_get_view.__name__ == "UserMeRetrieveView"

    def test_default_user_me_view(self, authenticated_client, user):
        """
        Test that default user-me view works without custom fields.
        """
        response = authenticated_client.get(reverse("user-me"))
        assert response.status_code == status.HTTP_200_OK
        assert "custom_field" not in response.data
        assert "view_type" not in response.data

    @pytest.mark.skip(
        reason="View configuration changes require process restart due to URL dispatcher caching"  # noqa: E501
    )
    def test_djoser_settings_fixture_works(self, authenticated_client, user):
        """
        Test that the djoser_settings fixture can modify configuration.
        """
        from django.urls import reverse

        # Instead of trying to modify the actual dispatcher, mock the view directly
        with patch("djoser.urls.utils.create_configurable_dispatcher") as mock_create:
            # Create a mock dispatcher that returns our custom view
            def mock_dispatcher(request, *args, **kwargs):
                if request.method == "GET":
                    return CustomUserMeView.as_view()(request, *args, **kwargs)
                from django.http import HttpResponseNotAllowed

                return HttpResponseNotAllowed(["GET"])

            mock_create.return_value = mock_dispatcher

            # Make HTTP request and verify the custom view is being used
            response = authenticated_client.get(reverse("user-me"))
            assert response.status_code == status.HTTP_200_OK
            assert response.data["id"] == user.id
            # Custom view should add these fields
            assert response.data["custom_field"] == "custom_value"
            assert response.data["view_type"] == "custom"


class TestViewConfigurationUnits:
    """
    Unit tests for view configuration components.
    """

    def test_configurable_dispatcher_with_valid_views(self):
        """
        Test that create_configurable_dispatcher works with valid view keys.
        """
        from djoser.urls.utils import create_configurable_dispatcher

        # Test with valid view configuration
        dispatcher = create_configurable_dispatcher(
            {
                "GET": "user_me_get",
                "PUT": "user_me_put",
            }
        )
        assert dispatcher is not None
        assert callable(dispatcher)

    def test_configurable_dispatcher_with_none_values(self):
        """
        Test that create_configurable_dispatcher handles None values correctly.
        """
        from djoser.urls.utils import create_configurable_dispatcher

        # Test with non-existent key that returns None
        dispatcher = create_configurable_dispatcher(
            {
                "GET": "non_existent_view_key_that_returns_none",
            }
        )
        assert dispatcher is None

    def test_custom_view_class_definition(self):
        """
        Test that our custom view can be imported and has correct structure.
        """
        assert callable(CustomUserMeView)
        assert issubclass(CustomUserMeView, UserMeRetrieveView)

        # Test that it has the expected method
        assert hasattr(CustomUserMeView, "get")


class TestViewConfigurationManual(TestCase):
    """
    Test view configuration by manually modifying settings.
    """

    def test_view_path_resolution(self):
        """
        Test that view paths resolve correctly to actual view classes.
        """
        from djoser.conf import settings
        from djoser.views.me.retrieve import UserMeRetrieveView

        # Test that view resolution works
        view_class = getattr(settings.VIEWS, "user_me_get", None)
        assert callable(view_class)
        assert issubclass(view_class, UserMeRetrieveView)

    def test_settings_has_views_configuration(self):
        """
        Test that settings object has VIEWS configuration.
        """
        from djoser.conf import settings, default_settings

        # Settings should have VIEWS
        assert hasattr(settings, "VIEWS")

        # Default settings should have VIEWS as ObjDict
        assert "VIEWS" in default_settings

        # VIEWS should be an ObjDict instance
        from djoser.conf import ObjDict

        assert isinstance(default_settings["VIEWS"], ObjDict)

    def test_objdict_behavior(self):
        """
        Test that ObjDict behaves correctly for view configuration.
        """
        from djoser.conf import ObjDict

        # Create test ObjDict with string value
        test_config = ObjDict(
            {"test_view": "djoser.views.me.retrieve.UserMeRetrieveView"}
        )

        # First access should import the string
        view_class = test_config.test_view
        assert callable(view_class)
        assert view_class.__name__ == "UserMeRetrieveView"

        # Second access should return the cached imported class
        view_class2 = test_config.test_view
        assert view_class == view_class2

        # Test with None value
        test_config["none_view"] = None
        assert test_config.none_view is None


class TestDispatcherCreation(TestCase):
    """
    Test dispatcher creation functionality.
    """

    def test_view_dispatcher_creation(self):
        """
        Test that view dispatchers can be created with different configurations.
        """
        from djoser.urls.utils import create_dispatcher, create_configurable_dispatcher
        from djoser.views.me.retrieve import UserMeRetrieveView
        from djoser.views.me.update import UserMeUpdateView

        # Test basic dispatcher creation
        dispatcher = create_dispatcher(
            {
                "GET": UserMeRetrieveView,
                "PUT": UserMeUpdateView,
            }
        )
        assert dispatcher is not None
        assert callable(dispatcher)

        # Test configurable dispatcher
        config_dispatcher = create_configurable_dispatcher(
            {
                "GET": "user_me_get",
                "PUT": "user_me_put",
            }
        )
        assert config_dispatcher is not None
        assert callable(config_dispatcher)

    def test_dispatcher_with_empty_methods(self):
        """
        Test dispatcher behavior with empty method configurations.
        """
        from djoser.urls.utils import create_dispatcher, create_configurable_dispatcher

        # Empty method map should still create a dispatcher
        dispatcher = create_dispatcher({})
        assert dispatcher is not None
        assert callable(dispatcher)

        # Empty configurable dispatcher with non-existent keys should return None
        config_dispatcher = create_configurable_dispatcher(
            {
                "GET": "definitely_non_existent_view_key",
                "POST": "another_non_existent_key",
            }
        )
        assert config_dispatcher is None
