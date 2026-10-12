from rest_framework import serializers, status, views
from rest_framework.response import Response

from djoser import utils
from djoser.conf import settings


class TokenDestroyView(views.APIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """

    serializer_class = serializers.Serializer
    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
