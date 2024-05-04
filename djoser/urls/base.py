from django.urls import path
from rest_framework.routers import DefaultRouter

from djoser.views import UserViewSet as OldUserViewSet
from djoser.views.user.me import UserMeViewSet
from djoser.views.user.user import UserViewSet

old_router = DefaultRouter()
old_router.register("users-old", OldUserViewSet)

user_list = path(
    "users/", UserViewSet.as_view({"get": "list", "post": "create"}), name="user-list"
)
user_detail = path(
    f"users/<{UserViewSet.lookup_field}>/",
    UserViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    ),
    name="user-detail",
)
me_list = path(
    "users/me/",
    UserMeViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    ),
    name="user-me",
)
urlpatterns = [
    *old_router.urls,
    me_list,
    user_list,
    user_detail,
]
