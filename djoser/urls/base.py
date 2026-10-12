from rest_framework.urlpatterns import format_suffix_patterns

from djoser.urls.activation import (
    user_activation,
    user_resend_activation,
)
from djoser.urls.me import me_list
from djoser.urls.me import schema_urlpatterns as me_schema_urlpatterns
from djoser.urls.password import (
    user_password_reset_confirm,
    user_reset_password,
    user_set_password,
)
from djoser.urls.user import (
    user_detail_update_delete,
    user_list_create,
)
from djoser.urls.user import schema_urlpatterns as user_schema_urlpatterns
from djoser.urls.username import (
    user_reset_username,
    user_reset_username_confirm,
    user_set_username,
)


# format_suffix_patterns adds the .json/.api routes DRF's DefaultRouter generated,
# e.g. /users/1.json. It relies on the lookup regex excluding dots.
urlpatterns = format_suffix_patterns(
    [
        user_resend_activation,
        user_activation,
        user_password_reset_confirm,
        user_reset_username_confirm,
        user_reset_password,
        user_set_password,
        user_set_username,
        user_reset_username,
        me_list,
        user_detail_update_delete,
        user_list_create,
    ]
)

# Only seen by schema generators; see schema_patterns().
urlpatterns += user_schema_urlpatterns + me_schema_urlpatterns
