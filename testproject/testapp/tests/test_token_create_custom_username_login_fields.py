from unittest import mock

import pytest
from django.contrib.auth import user_logged_in, user_login_failed
from django.contrib.auth.backends import ModelBackend
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
class BaseTestUsernameLoginFields:
    url = reverse("login")

    @pytest.fixture(autouse=True)
    def add_authentication_backend(self, settings):
        raise NotImplementedError

    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.AUTHENTICATION_BACKENDS = [
            "django.contrib.auth.backends.ModelBackend",
        ]
        return settings

    @pytest.fixture
    def signal_user_logged_in_patched(self):
        signal_handler = mock.MagicMock()
        user_logged_in.connect(signal_handler)
        return signal_handler

    @pytest.fixture
    def signal_user_login_failed_patched(self):
        signal_handler = mock.MagicMock()
        user_login_failed.connect(signal_handler)
        return signal_handler

    def configure_djoser_settings(
        self,
        djoser_settings,
        mocker,
        login_field,
        username_field,
        user_can_authenticate,
    ):
        djoser_settings["LOGIN_FIELD"] = login_field
        mocker.patch("djoser.serializers.User.USERNAME_FIELD", username_field)
        mocker.patch.object(
            ModelBackend, "user_can_authenticate", return_value=user_can_authenticate
        )

    def _test_successful_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_logged_in_patched,
        login_field,
        username_field,
        send_field,
    ):
        self.configure_djoser_settings(
            djoser_settings=djoser_settings,
            mocker=mocker,
            login_field=login_field,
            username_field=username_field,
            user_can_authenticate=True,
        )

        if send_field == "username":
            data = {"username": user.username, "password": user.raw_password}
        else:
            data = {"email": user.email, "password": user.raw_password}

        previous_last_login = user.last_login
        response = client.post(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()

        assert response.data["auth_token"] == user.auth_token.key
        assert user.last_login != previous_last_login
        signal_user_logged_in_patched.assert_called_once()

    def _test_failing_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_login_failed_patched,
        login_field,
        username_field,
        send_field,
        user_can_authenticate,
    ):
        self.configure_djoser_settings(
            djoser_settings=djoser_settings,
            mocker=mocker,
            login_field=login_field,
            username_field=username_field,
            user_can_authenticate=user_can_authenticate,
        )
        if send_field == "username":
            data = {"username": user.username, "password": user.raw_password}
        else:
            data = {"email": user.email, "password": user.raw_password}

        previous_last_login = user.last_login
        response = client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()

        assert user.last_login == previous_last_login
        signal_user_login_failed_patched.assert_called_once()


@pytest.mark.django_db
class TestModelBackendLoginFields(BaseTestUsernameLoginFields):
    url = reverse("login")

    @pytest.fixture(autouse=True)
    def add_authentication_backend(self, settings):
        settings.AUTHENTICATION_BACKENDS = [
            "django.contrib.auth.backends.ModelBackend",
        ]

    @pytest.mark.parametrize(
        "login_field, username_field, send_field",
        [
            ("username", "username", "username"),
            ("email", "email", "email"),
        ],
    )
    def test_successful_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_logged_in_patched,
        login_field,
        username_field,
        send_field,
    ):
        self._test_successful_login(
            user,
            client,
            djoser_settings,
            mocker,
            signal_user_logged_in_patched,
            login_field,
            username_field,
            send_field,
        )

    @pytest.mark.parametrize(
        "login_field, username_field, user_can_authenticate, send_field",
        [
            ("username", "username", False, "username"),
            ("username", "username", True, "email"),
            ("username", "email", True, "username"),
            ("username", "email", False, "username"),
            ("email", "username", False, "username"),
            ("email", "username", True, "email"),
            ("email", "email", True, "username"),
            ("email", "email", False, "username"),
            ("username", "email", True, "email"),
            ("email", "username", True, "username"),
        ],
    )
    def test_failing_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_login_failed_patched,
        login_field,
        username_field,
        send_field,
        user_can_authenticate,
    ):
        self._test_failing_login(
            user,
            client,
            djoser_settings,
            mocker,
            signal_user_login_failed_patched,
            login_field,
            username_field,
            send_field,
            user_can_authenticate,
        )


@pytest.mark.django_db
class TestLoginFieldBackend(BaseTestUsernameLoginFields):
    url = reverse("login")

    @pytest.fixture(autouse=True)
    def add_authentication_backend(self, settings):
        settings.AUTHENTICATION_BACKENDS = [
            "djoser.auth_backends.LoginFieldBackend",
        ]

    @pytest.mark.parametrize(
        "login_field, username_field, send_field",
        [
            ("username", "username", "username"),
            ("email", "email", "email"),
            ("email", "username", "email"),
            ("username", "email", "username"),
        ],
    )
    def test_successful_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_logged_in_patched,
        login_field,
        username_field,
        send_field,
    ):
        self._test_successful_login(
            user,
            client,
            djoser_settings,
            mocker,
            signal_user_logged_in_patched,
            login_field,
            username_field,
            send_field,
        )

    @pytest.mark.parametrize(
        "login_field, username_field, user_can_authenticate, send_field",
        [
            ("username", "username", False, "username"),
            ("username", "email", False, "username"),
            ("email", "username", False, "username"),
            ("email", "email", False, "username"),
            ("username", "username", True, "email"),
            ("email", "email", True, "username"),
            ("username", "email", True, "email"),
            ("email", "username", True, "username"),
        ],
    )
    def test_failing_login(
        self,
        user,
        client,
        djoser_settings,
        mocker,
        signal_user_login_failed_patched,
        login_field,
        username_field,
        send_field,
        user_can_authenticate,
    ):
        self._test_failing_login(
            user,
            client,
            djoser_settings,
            mocker,
            signal_user_login_failed_patched,
            login_field,
            username_field,
            send_field,
            user_can_authenticate,
        )

    def test_user_does_not_exist(self, client, djoser_settings, mocker):
        self.configure_djoser_settings(
            djoser_settings=djoser_settings,
            mocker=mocker,
            login_field="username",
            username_field="username",
            user_can_authenticate=True,
        )
        data = {"username": "idontexist1337", "password": "P455W0RD"}

        response = client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
