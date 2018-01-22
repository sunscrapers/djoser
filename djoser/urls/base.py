from django.conf.urls import include, url
from django.contrib.auth import get_user_model

from rest_framework.routers import DefaultRouter, Route

from djoser import views

User = get_user_model()


class OptionalSlashRouter(DefaultRouter):
    def __init__(self):
        super(OptionalSlashRouter, self).__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.routes.append(Route(
    url=r'^user{trailing_slash}$',
    mapping={
        'delete': 'remove',
        'get': 'me',
        'put': 'update',
    },
    name='{basename}-instance',
    initkwargs={'suffix': 'Instance'}
))
router.register(
    r'user/{}'.format(User.USERNAME_FIELD),
    views.UsernameUpdateViewSet,
    base_name='username-update',
)
router.register(
    r'user/password',
    views.PasswordUpdateViewSet,
    base_name='password-reset',
)
router.register(
    r'password/reset',
    views.PasswordResetConfirmViewSet,
    base_name='password-reset-confirm',
)
router.register(
    r'user',
    views.UserViewSet,
    base_name='user',
)
router.register(
    r'users',
    views.UsersViewSet,
    base_name='users',
)
router.register(
    r'users/activate',
    views.UserActivateViewSet,
    base_name='user-activate',
)

urlpatterns = [
    url(r'^', include(router.urls)),
]
