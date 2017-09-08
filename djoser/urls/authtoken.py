from django.conf.urls import url

from djoser import views


urlpatterns = [
    url(r'^token/create$', views.LoginView.as_view(), name='login'),
    url(r'^token/destroy$', views.LogoutView.as_view(), name='logout'),
]
