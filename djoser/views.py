from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from djoser.conf import settings

User = get_user_model()


def run_pipeline(request, steps):
    return settings.VIEW_PIPELINE_ADAPTER(request, steps)


class UsersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['user_create']
        response_data = run_pipeline(request, steps)
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def me(self, request, *args, **kwargs):
        steps = settings.PIPELINES['user_detail']
        response_data = run_pipeline(request, steps)
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        steps = settings.PIPELINES['user_update']
        response_data = run_pipeline(request, steps)
        return Response(response_data, status=status.HTTP_200_OK)

    def remove_user(self, request, *args, **kwargs):
        steps = settings.PIPELINES['user_delete']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserActivateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['user_activate']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsernameUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['username_update']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['password_update']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['password_reset']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['password_reset_confirm']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        steps = settings.PIPELINES['token_create']
        response_data = run_pipeline(request, steps)
        return Response(response_data, status=status.HTTP_201_CREATED)

    def remove_token(self, request, *args, **kwargs):
        steps = settings.PIPELINES['token_delete']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)
