from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^register$', views.RegistrationView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^activate$', views.PasswordResetConfirmView.as_view(), name='activate'),
    url(r'^username$', views.SetUsernameView.as_view(), name='set_username'),
    url(r'^password', views.SetPasswordView.as_view(), name='set_password'),
    url(r'^password/reset$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/confirm$', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
)