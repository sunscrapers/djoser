from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter

from djoser import views

router = DefaultRouter()
router.register("users", views.UserViewSet)

User = get_user_model()

urlpatterns = router.urls
