from django.conf.urls import patterns, url
from . import views
from django.contrib.auth import get_user_model

User = get_user_model()

urlpatterns = patterns('',
                       url(r'^$', views.RootView.as_view(), name='root'),
                       url(r'^me/$', views.UserView.as_view(), name='user'),
                       url(r'^register/$', views.RegistrationView.as_view(), name='register'),
                       url(r'^login/$', views.LoginView.as_view(), name='login'),
                       url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
                       url(r'^activate/$', views.ActivationView.as_view(), name='activate'),
                       url(r'^{0}/$'.format(User.USERNAME_FIELD), views.SetUsernameView.as_view(), name='set_username'),
                       url(r'^password/$', views.SetPasswordView.as_view(), name='set_password'),
                       url(r'^password/reset/$', views.PasswordResetView.as_view(), name='password_reset'),
                       url(r'^password/reset/confirm/$', views.PasswordResetConfirmView.as_view(),
                           name='password_reset_confirm'),
                       )
