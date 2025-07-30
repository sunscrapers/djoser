from djoser.urls.activation import (
    user_activation,
    user_resend_activation,
)
from djoser.urls.me import me_list
from djoser.urls.password import (
    user_password_reset_confirm,
    user_reset_password,
    user_set_password,
)
from djoser.urls.user import (
    user_detail_update_delete,
    user_list_create,
)
from djoser.urls.username import (
    user_reset_username,
    user_reset_username_confirm,
    user_set_username,
)


urlpatterns = [
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
