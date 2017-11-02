from rest_framework import generics, permissions
from rest_framework.response import Response

from social_django.utils import load_backend, load_strategy

from djoser.social.serializers import ProviderAuthSerializer


class ProviderAuthView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProviderAuthSerializer

    def get(self, request, *args, **kwargs):
        redirect_uri = request.GET.get('redirect_uri') or 'http://localhost/'
        strategy = load_strategy(request)
        strategy.session_set('redirect_uri', redirect_uri)

        backend_name = self.kwargs['provider']
        backend = load_backend(
            strategy, backend_name, redirect_uri=redirect_uri

        )
        authorization_url = backend.auth_url()
        return Response(data={
            'authorization_url': authorization_url,
        })
