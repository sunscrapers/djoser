from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from djoser import pipelines
from djoser.conf import settings

User = get_user_model()


def run_pipeline(pipeline, request):
    return settings.VIEW_PIPELINE_ADAPTER(pipeline, request)


class UsersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_create.Pipeline
        response_data = run_pipeline(pipeline, request)
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def me(self, request, *args, **kwargs):
        pipeline = pipelines.user_detail.Pipeline
        response_data = run_pipeline(pipeline, request)
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pipeline = pipelines.user_update.Pipeline
        response_data = run_pipeline(pipeline, request)
        return Response(response_data, status=status.HTTP_200_OK)

    def remove(self, request, *args, **kwargs):
        pipeline = pipelines.user_delete.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserActivateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_activate.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsernameUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.username_update.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordUpdateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_update.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset_confirm.Pipeline
        run_pipeline(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)
