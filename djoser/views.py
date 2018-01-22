from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from djoser import pipelines

User = get_user_model()


class UsersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_create.Pipeline(request)
        response_data = pipeline.run()['response_data']
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def me(self, request, *args, **kwargs):
        pipeline = pipelines.user_detail.Pipeline(request)
        response_data = pipeline.run()['response_data']
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pipeline = pipelines.user_update.Pipeline(request)
        response_data = pipeline.run()['response_data']
        return Response(response_data, status=status.HTTP_200_OK)

    def remove(self, request, *args, **kwargs):
        pipeline = pipelines.user_delete.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserActivateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_activate.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsernameUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.username_update.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_update.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset_confirm.Pipeline(request)
        pipeline.run()
        return Response(status=status.HTTP_204_NO_CONTENT)
