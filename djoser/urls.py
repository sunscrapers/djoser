from django.conf.urls import include, url
from django.contrib.auth import get_user_model

from rest_framework.routers import DefaultRouter, DynamicListRoute, Route

from djoser import views

User = get_user_model()


class DjoserRouter(DefaultRouter):
    def __init__(self, include_token_urls=False):
        super(DjoserRouter, self).__init__()
        self.trailing_slash = '/?'

        self._insert_routes()
        self._register_urls(include_token_urls)

    def _insert_routes(self):
        self.routes.insert(0, Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'delete': 'remove_user',
                'get': 'me',
                'put': 'update',
            },
            name='{basename}-instance',
            initkwargs={'suffix': 'Instance'}
        ))
        self.routes.insert(0, Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'delete': 'remove_token',
                'post': 'create',
            },
            name='{basename}-instance',
            initkwargs={'suffix': 'Instance'}
        ))

    def _register_urls(self, include_token_urls):
        if include_token_urls:
            self.register(
                r'^token',
                views.TokenViewSet,
                base_name='token',
            )

        self.register(
            r'^user/{}'.format(User.USERNAME_FIELD),
            views.UsernameUpdateViewSet,
            base_name='username-update',
        )
        self.register(
            r'^user/password',
            views.PasswordUpdateViewSet,
            base_name='password-update',
        )
        self.register(
            r'^password/reset',
            views.PasswordResetViewSet,
            base_name='password-reset',
        )
        self.register(
            r'^password/reset/confirm',
            views.PasswordResetConfirmViewSet,
            base_name='password-reset-confirm',
        )
        self.register(
            r'^user',
            views.UserViewSet,
            base_name='user',
        )
        self.register(
            r'^users',
            views.UsersViewSet,
            base_name='users'
        )
        self.register(
            r'^users/activate',
            views.UserActivateViewSet,
            base_name='user-activate',
        )


router = DjoserRouter()


urlpatterns = [
    url(r'^', include(router.urls)),
]
