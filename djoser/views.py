from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from djoser.conf import settings

User = get_user_model()


def run_pipeline(request, steps):
    return settings.VIEW_PIPELINE_ADAPTER(request, steps)


class PipelineMixin:
    def create(self, request, *args, **kwargs):
        steps = self.pipeline
        run_pipeline(request, steps)
        return Response(status=self.status_code)


class UsersViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    pipeline = settings.PIPELINES['user_create']
    status_code = status.HTTP_201_CREATED


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


class UserActivateViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    pipeline = settings.PIPELINES['user_activate']
    status_code = status.HTTP_204_NO_CONTENT


class UsernameUpdateViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pipeline = settings.PIPELINES['username_update']
    status_code = status.HTTP_204_NO_CONTENT


class PasswordUpdateViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pipeline = settings.PIPELINES['password_update']
    status_code = status.HTTP_204_NO_CONTENT


class PasswordResetViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    pipeline = settings.PIPELINES['password_reset']
    status_code = status.HTTP_204_NO_CONTENT


class PasswordResetConfirmViewSet(PipelineMixin, viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    pipeline = settings.PIPELINES['password_reset_confirm']
    status_code = status.HTTP_204_NO_CONTENT


class TokenViewSet(PipelineMixin, viewsets.ViewSet):
    pipeline = settings.PIPELINES['token_create']
    status_code = status.HTTP_201_CREATED

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

    def remove_token(self, request, *args, **kwargs):
        steps = settings.PIPELINES['token_delete']
        run_pipeline(request, steps)
        return Response(status=status.HTTP_204_NO_CONTENT)
