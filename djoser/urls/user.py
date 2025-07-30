from django.urls import path

from djoser.urls.utils import create_configurable_dispatcher

# Create configurable dispatchers for user endpoints
user_list_create_dispatcher = create_configurable_dispatcher(
    {
        "GET": "user_list",
        "POST": "user_create",
    }
)

user_detail_dispatcher = create_configurable_dispatcher(
    {
        "GET": "user_detail",
        "PUT": "user_update",
        "PATCH": "user_update",
        "DELETE": "user_delete",
    }
)

urlpatterns = []

if user_list_create_dispatcher:
    user_list_create = path(
        "users/",
        user_list_create_dispatcher,
        name="user-list",
    )
    urlpatterns.append(user_list_create)

if user_detail_dispatcher:
    # Import to get lookup field - only if needed
    from djoser.views.user import UserRetrieveView

    user_detail_update_delete = path(
        f"users/<{UserRetrieveView.lookup_field}>/",
        user_detail_dispatcher,
        name="user-detail",
    )
    urlpatterns.append(user_detail_update_delete)
