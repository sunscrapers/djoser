from django.urls import re_path

from djoser.urls.utils import (
    create_configurable_dispatcher,
    schema_patterns,
    user_url_name,
)

# Create configurable dispatcher for user "me" endpoint
me_dispatcher = create_configurable_dispatcher(
    {
        "GET": "user_me_get",
        "PUT": "user_me_put",
        "PATCH": "user_me_patch",
        "DELETE": "user_me_delete",
    }
)

urlpatterns = []
schema_urlpatterns = []

if me_dispatcher:
    me_list = re_path(r"^users/me/$", me_dispatcher, name=user_url_name("me"))
    urlpatterns.append(me_list)
    schema_urlpatterns += schema_patterns(r"^users/me/$", me_dispatcher)
