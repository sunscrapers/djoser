Examples
========


Early detecting invalid password reset tokens
---------------------------------------------

When there is need to check if password reset token is still valid without
actually resetting the password it is possible to approach the problem like so:

.. code-block:: python

    from django.contrib.auth.tokens import default_token_generator
    from rest_framework import generics, permissions, status
    from rest_framework.response import Response

    from djoser import serializers


    class PasswordTokenCheckView(generics.CreateAPIView):
        permission_classes = (
            permissions.AllowAny,
        )
        token_generator = default_token_generator
        serializer_class = serializers.UidAndTokenSerializer

        def post(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)