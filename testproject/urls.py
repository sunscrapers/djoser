from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^auth/', include('djoser.urls.authtoken')),
)
