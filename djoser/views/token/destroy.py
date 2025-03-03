from rest_framework import status, generics, serializers
from rest_framework.response import Response

from djoser import utils
from djoser.conf import settings


class TokenDestroyView(generics.GenericAPIView):
    """Use this endpoint to logout user (remove user authentication token)."""

    serializer_class = serializers.Serializer
    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
