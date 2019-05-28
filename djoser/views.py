from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.timezone import now
from rest_framework import (
    generics,
    status, views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser import utils, signals
from djoser.compat import get_user_email
from djoser.conf import settings

User = get_user_model()


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """
    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_200_OK,
        )


class TokenDestroyView(views.APIView):
    """
    Use this endpoint to logout user (remove user authentication token).
    """
    permission_classes = settings.PERMISSIONS.token_destroy

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            qs = qs.filter(pk=user.pk)
        return qs

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == 'confirm':
            self.permission_classes = settings.PERMISSIONS.activation
        elif self.action == 'resend_activation':
            self.permission_classes = settings.PERMISSIONS.password_reset
        elif self.action == 'list':
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == 'reset_password':
            self.permission_classes = settings.PERMISSIONS.password_reset
        elif self.action == 'reset_password_confirm':
            self.permission_classes = \
                settings.PERMISSIONS.password_reset_confirm
        elif self.action == 'set_password':
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == 'set_username':
            self.permission_classes = settings.PERMISSIONS.set_username
        elif self.action == 'reset_username':
            self.permission_classes = settings.PERMISSIONS.username_reset
        elif self.action == 'reset_username_confirm':
            self.permission_classes = \
                settings.PERMISSIONS.username_reset_confirm
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        elif self.action == 'remove' or (
                self.action == 'me' and self.request and
                self.request.method == 'DELETE'
        ):
            return settings.SERIALIZERS.user_delete
        elif self.action == 'confirm':
            return settings.SERIALIZERS.activation
        elif self.action == 'resend_activation':
            return settings.SERIALIZERS.password_reset
        elif self.action == 'reset_password':
            return settings.SERIALIZERS.password_reset
        elif self.action == 'reset_password_confirm':
            if settings.PASSWORD_RESET_CONFIRM_RETYPE:
                return settings.SERIALIZERS.password_reset_confirm_retype
            return settings.SERIALIZERS.password_reset_confirm
        elif self.action == 'set_password':
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        elif self.action == 'set_username':
            if settings.SET_USERNAME_RETYPE:
                return settings.SERIALIZERS.set_username_retype
            return settings.SERIALIZERS.set_username
        elif self.action == 'reset_username':
            return settings.SERIALIZERS.username_reset
        elif self.action == 'reset_username_confirm':
            if settings.PASSWORD_RESET_CONFIRM_RETYPE:
                return settings.SERIALIZERS.username_reset_confirm_retype
            return settings.SERIALIZERS.username_reset_confirm
        elif self.action == 'me':
            # Use the current user serializer on 'me' endpoints
            return settings.SERIALIZERS.current_user

        return self.serializer_class

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        context = {'user': user}
        to = [get_user_email(user)]
        if settings.SEND_ACTIVATION_EMAIL:
            settings.EMAIL.activation(self.request, context).send(to)
        elif settings.SEND_CONFIRMATION_EMAIL:
            settings.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        user = serializer.instance
        # should we send activation email after update?
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {'user': user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

    def perform_destroy(self, instance):
        utils.logout_user(self.request)
        super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get', 'put', 'patch', 'delete'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)
        elif request.method == 'PUT':
            return self.update(request, *args, **kwargs)
        elif request.method == 'PATCH':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            return self.destroy(request, *args, **kwargs)

    @action(['post'], detail=False)
    def confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {'user': user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        context = {'user': user}
        to = [get_user_email(user)]
        settings.EMAIL.activation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        context = {'user': user}
        to = [get_user_email(user)]
        settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data['new_password'])
        if hasattr(serializer.user, 'last_login'):
            serializer.user.last_login = now()
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def set_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        new_username = serializer.data['new_' + User.USERNAME_FIELD]

        setattr(user, User.USERNAME_FIELD, new_username)
        # Add reset username, similar to reset_password
        # if settings.SEND_ACTIVATION_EMAIL:
        #     user.is_active = False
        #     context = {'user': user}
        #     to = [get_user_email(user)]
        #     settings.EMAIL.activation(self.request, context).send(to)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def reset_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        context = {'user': user}
        to = [get_user_email(user)]
        settings.EMAIL.username_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'], detail=False)
    def reset_username_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        new_username = serializer.data['new_' + User.USERNAME_FIELD]

        setattr(user, User.USERNAME_FIELD, new_username)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
