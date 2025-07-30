from django.urls import path

from djoser.urls.utils import create_configurable_dispatcher

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

if me_dispatcher:
    me_list = path(
        "users/me/",
        me_dispatcher,
        name="user-me",
    )
    urlpatterns.append(me_list)
