from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^register/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^password/reset$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/set$', views.SetPasswordView.as_view(), name='set_password'),
)