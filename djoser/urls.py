from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^register$', views.RegistrationView.as_view(), name='register'),
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^activate$', views.PasswordResetConfirmView.as_view(), name='activate'),
    url(r'^password/reset$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/confirm$', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
)