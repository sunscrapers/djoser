from django.conf.urls import url

from djoser.social import views


urlpatterns = [
    url(
        r'^o/(?P<provider>\S+)/$',
        views.ProviderAuthView.as_view(),
        name='provider-auth'
    ),
]
