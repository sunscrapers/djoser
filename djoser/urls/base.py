from django.conf.urls import url, include
from django.contrib.auth import get_user_model

from djoser import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserViewSet)

User = get_user_model()

urlpatterns = [
    url(r'^me/?$', views.UserView.as_view(), name='user'),
    url(
        r'^users/create/?$',
        views.UserCreateView.as_view(),
        name='user-create'
    ),
    url(
        r'^users/delete/?$',
        views.UserDeleteView.as_view(),
        name='user-delete'
    ),
    url(
        r'^users/activate/?$',
        views.ActivationView.as_view(),
        name='user-activate'
    ),
    url(
        r'^{0}/?$'.format(User.USERNAME_FIELD),
        views.SetUsernameView.as_view(),
        name='set_username'
    ),
    url(r'^password/?$', views.SetPasswordView.as_view(), name='set_password'),
    url(
        r'^password/reset/?$',
        views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    url(
        r'^password/reset/confirm/?$',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    url(r'^$', views.RootView.as_view(), name='root'),
    url(r'^', include(router.urls)),
]
