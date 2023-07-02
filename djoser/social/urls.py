from django.urls import path

from djoser.social import views

urlpatterns = [
    path(
        "o/<provider>/",
        views.ProviderAuthView.as_view(),
        name="provider-auth",
    )
]
