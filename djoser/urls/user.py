from django.urls import re_path

from djoser.urls.utils import (
    create_configurable_dispatcher,
    schema_patterns,
    user_url_name,
)

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
        "PUT": "user_update_put",
        "PATCH": "user_update_patch",
        "DELETE": "user_delete",
    }
)

urlpatterns = []
schema_urlpatterns = []

if user_list_create_dispatcher:
    user_list_create = re_path(
        r"^users/$",
        user_list_create_dispatcher,
        name=user_url_name("list"),
    )
    urlpatterns.append(user_list_create)
    schema_urlpatterns += schema_patterns(r"^users/$", user_list_create_dispatcher)

if user_detail_dispatcher:
    # Import to get lookup field - only if needed
    from djoser.views.user.retrieve import UserRetrieveView

    # The lookup excludes dots, like 2.x's router, so /users/1.json is the format
    # suffix route rather than a lookup value of "1.json".
    user_detail_regex = rf"^users/(?P<{UserRetrieveView.lookup_field}>[^/.]+)/$"
    user_detail_update_delete = re_path(
        user_detail_regex,
        user_detail_dispatcher,
        name=user_url_name("detail"),
    )
    urlpatterns.append(user_detail_update_delete)
    schema_urlpatterns += schema_patterns(user_detail_regex, user_detail_dispatcher)
