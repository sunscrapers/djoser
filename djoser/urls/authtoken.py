from django.conf.urls import url

from djoser import views


urlpatterns = [
    url(
        r'^token/create/?$',
        views.TokenCreateView.as_view(),
        name='token-create'
    ),
    url(
        r'^token/destroy/?$',
        views.TokenDestroyView.as_view(),
        name='token-destroy'
    ),
    url(
        r'^token/login/?$',
        views.TokenCreateView.as_view(),
        name='login'
    ),
    url(
        r'^token/logout/?$',
        views.TokenDestroyView.as_view(),
        name='logout'
    ),
]
