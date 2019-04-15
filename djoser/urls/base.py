from django.conf.urls import url, include
from django.contrib.auth import get_user_model

from djoser import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserViewSet)

User = get_user_model()

urlpatterns = [
    url(
        r'^users/resend/?$',
        views.ResendActivationView.as_view(),
        name='user-activate-resend'
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
    url(r'^', include(router.urls)),
]
