from rest_framework.routers import DefaultRouter


from djoser.views import UserViewSet as OldUserViewSet
from djoser.views.user.user import UserViewSet

old_router = DefaultRouter()
old_router.register("users-old", OldUserViewSet)

router = DefaultRouter()
router.register("users", UserViewSet)

# User = get_user_model()

# users_url = path("users/", ListCreateUserView.as_view(), name="user-list")

urlpatterns = [
    # users_url,
    *old_router.urls,
    *router.urls,
]
