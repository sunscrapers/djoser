from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from djoser import pipelines
from djoser.conf import settings

User = get_user_model()


class BasePipelineViewSet(viewsets.ViewSet):
    view_pipeline_adapter = settings.VIEW_PIPELINE_ADAPTER

    def run(self, pipeline, request):
        return BasePipelineViewSet.view_pipeline_adapter(pipeline, request)


class UsersViewSet(BasePipelineViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_create.Pipeline
        response_data = self.run(pipeline, request)
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(BasePipelineViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def me(self, request, *args, **kwargs):
        pipeline = pipelines.user_detail.Pipeline
        response_data = self.run(pipeline, request)
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pipeline = pipelines.user_update.Pipeline
        response_data = self.run(pipeline, request)
        return Response(response_data, status=status.HTTP_200_OK)

    def remove(self, request, *args, **kwargs):
        pipeline = pipelines.user_delete.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserActivateViewSet(BasePipelineViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.user_activate.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsernameUpdateViewSet(BasePipelineViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.username_update.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordUpdateViewSet(BasePipelineViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_update.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetViewSet(BasePipelineViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmViewSet(BasePipelineViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        pipeline = pipelines.password_reset_confirm.Pipeline
        self.run(pipeline, request)
        return Response(status=status.HTTP_204_NO_CONTENT)
