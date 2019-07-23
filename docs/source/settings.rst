Settings
========

You can provide ``DJOSER`` settings like this:

.. code-block:: python

    DJOSER = {
        'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
        'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
        'ACTIVATION_URL': '#/activate/{uid}/{token}',
        'SEND_ACTIVATION_EMAIL': True,
        'SERIALIZERS': {},
    }

.. note::

    All following setting names written in CAPS are keys on ``DJOSER`` dict.


LOGIN_FIELD
-----------

Name of a field in User model to be used as login field. This is useful if you
want to change the login field from ``username`` to ``email`` without providing
custom User model.

**Default**: ``User.USERNAME_FIELD`` where ``User`` is the model set with Django's setting AUTH_USER_MODEL.

PASSWORD_RESET_CONFIRM_URL
--------------------------

URL to your frontend password reset page. It should contain ``{uid}`` and
``{token}`` placeholders, e.g. ``#/password-reset/{uid}/{token}``.
You should pass ``uid`` and ``token`` to reset password confirmation endpoint.

**Required**: ``True``

USERNAME_RESET_CONFIRM_URL
--------------------------

URL to your frontend username reset page. It should contain ``{uid}`` and
``{token}`` placeholders, e.g. ``#/username-reset/{uid}/{token}``.
You should pass ``uid`` and ``token`` to reset username confirmation endpoint.

**Required**: ``True``

SEND_ACTIVATION_EMAIL
---------------------

If ``True`` user will be required to click activation link sent in email after:

* creating an account
* updating their email

**Default**: ``False``

SEND_CONFIRMATION_EMAIL
-----------------------

If ``True``, register or activation endpoint will send confirmation email to user.

**Default**: ``False``

PASSWORD_CHANGED_EMAIL_CONFIRMATION
-----------------------------------

If ``True``, change password endpoints will send confirmation email to user.

**Default**: ``False``

USERNAME_CHANGED_EMAIL_CONFIRMATION
-----------------------------------

If ``True``, change username endpoints will send confirmation email to user.

**Default**: ``False``

ACTIVATION_URL
--------------

URL to your frontend activation page. It should contain ``{uid}`` and ``{token}``
placeholders, e.g. ``#/activate/{uid}/{token}``. You should pass ``uid`` and
``token`` to activation endpoint.

**Required**: ``True``

USER_CREATE_PASSWORD_RETYPE
---------------------------

If ``True``, you need to pass ``re_password`` to
``/users/`` endpoint, to validate password equality.

**Default**: ``False``

SET_USERNAME_RETYPE
-------------------

If ``True``, you need to pass ``re_new_username`` to
``/users/set_username/`` endpoint, to validate username equality.

**Default**: ``False``

SET_PASSWORD_RETYPE
-------------------

If ``True``, you need to pass ``re_new_password`` to ``/users/set_password/``
endpoint, to validate password equality.

**Default**: ``False``

PASSWORD_RESET_CONFIRM_RETYPE
-----------------------------

If ``True``, you need to pass ``re_new_password`` to ``/users/reset_password_confirm/``
endpoint in order to validate password equality.

**Default**: ``False``

USERNAME_RESET_CONFIRM_RETYPE
-----------------------------

If ``True``, you need to pass ``re_new_username`` to
``/users/reset_username_confirm/`` endpoint in order to validate username equality.

**Default**: ``False``

LOGOUT_ON_PASSWORD_CHANGE
-------------------------

If ``True``, setting new password will logout the user.

**Default**: ``False``

.. note::

    Logout only works with token based authentication.

PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
-----------------------------------

If ``True``, posting a non-existent ``email`` to ``/users/reset_password/`` will return
a ``HTTP_400_BAD_REQUEST`` response with an ``EMAIL_NOT_FOUND`` error message
('User with given email does not exist.').

If ``False`` (default), the ``/users/reset_password/`` endpoint will always return
a ``HTTP_204_NO_CONTENT`` response.

Please note that setting this to ``True`` will expose information whether
an email is registered in the system.

**Default**: ``False``

USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
-----------------------------------

If ``True``, posting a non-existent ``email`` to ``/users/reset_username/`` will return
a ``HTTP_400_BAD_REQUEST`` response with an ``EMAIL_NOT_FOUND`` error message
('User with given email does not exist.').

If ``False`` (default), the ``/users/reset_username/`` endpoint will always return
a ``HTTP_204_NO_CONTENT`` response.

Please note that setting this to ``True`` will expose information whether
an email is registered in the system.

**Default**: ``False``

TOKEN_MODEL
-----------

Points to which token model should be used for authentication. In case if
only stateless tokens (e.g. JWT) are used in project it should be set to ``None``.

**Example**: ``'knox.models.AuthToken'``

**Default**: ``'rest_framework.authtoken.models.Token'``

SERIALIZERS
-----------

Dictionary which maps djoser serializer names to serializer classes (use dotted path).
This setting provides a way to easily override given serializer(s) - it is used
to update the defaults, so by providing, e.g. one key, all the others will stay default.

.. note::

    Key ``'user'`` is used for general users whereas ``'current_user'`` lets you set
    serializer for special ``/users/me`` endpoint. They both default to the same serializer though.

**Examples**

.. code-block:: python

    {
        'user': 'myapp.serializers.SpecialUserSerializer',
    }

**Default**:

.. code-block:: python

    {
        'activation': 'djoser.serializers.ActivationSerializer',
        'password_reset': 'djoser.serializers.SendEmailResetSerializer',
        'password_reset_confirm': 'djoser.serializers.PasswordResetConfirmSerializer',
        'password_reset_confirm_retype': 'djoser.serializers.PasswordResetConfirmRetypeSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'set_password_retype': 'djoser.serializers.SetPasswordRetypeSerializer',
        'set_username': 'djoser.serializers.SetUsernameSerializer',
        'set_username_retype': 'djoser.serializers.SetUsernameRetypeSerializer',
        'username_reset': 'djoser.serializers.SendEmailResetSerializer',
        'username_reset_confirm': 'djoser.serializers.UsernameResetConfirmSerializer',
        'username_reset_confirm_retype': 'djoser.serializers.UsernameResetConfirmRetypeSerializer',
        'user_create': 'djoser.serializers.UserCreateSerializer',
        'user_create_password_retype': 'djoser.serializers.UserCreatePasswordRetypeSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
        'user': 'djoser.serializers.UserSerializer',
        'current_user': 'djoser.serializers.CurrentUserSerializer',
        'token': 'djoser.serializers.TokenSerializer',
        'token_create': 'djoser.serializers.TokenCreateSerializer',
    }

EMAIL
-----

Dictionary which maps djoser email names to paths to email classes.
Same as in case of ``SERIALIZERS`` it allows partial override.

**Examples**

.. code-block:: python

    {
        'activation': 'myapp.email.AwesomeActivationEmail',
    }

**Default**:

.. code-block:: python

    {
        'activation': 'djoser.email.ActivationEmail',
        'confirmation': 'djoser.email.ConfirmationEmail',
        'password_reset': 'djoser.email.PasswordResetEmail',
        'password_changed_confirmation': 'djoser.email.PasswordChangedConfirmationEmail',
        'username_changed_confirmation': 'djoser.email.UsernameChangedConfirmationEmail',
        'username_reset': 'djoser.email.UsernameResetEmail',
    }

CONSTANTS
---------

Dictionary which maps djoser constant names to paths to constant classes.
Same as in case of ``SERIALIZERS`` it allows partial override.

**Examples**

.. code-block:: python

    {
        'messages': 'myapp.constants.CustomMessages',
    }

**Default**:

.. code-block:: python

    {
        'messages': 'djoser.constants.Messages',
    }

SOCIAL_AUTH_TOKEN_STRATEGY
--------------------------

String path to class responsible for token strategy used by social authentication.

**Example**: ``'myapp.token.MyStrategy'``

**Default**: ``'djoser.social.token.jwt.TokenStrategy'``

SOCIAL_AUTH_ALLOWED_REDIRECT_URIS
---------------------------------

List of allowed redirect URIs for social authentication.

**Example**: ``['https://auth.example.com']``

**Default**: ``[]``


.. _view-permission-settings:

PERMISSIONS
-----------

.. versionchanged:: 2.0

Dictionary that maps permissions to certain views across Djoser.

.. note::

    ``Admin`` in class names refers to users that have ``is_staff`` flag set to True,
    not superusers.


**Examples**

.. code-block:: python

    {
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly']
    }

**Defaults**

.. code-block:: python

    {
        'activation': ['rest_framework.permissions.AllowAny'],
        'password_reset': ['rest_framework.permissions.AllowAny'],
        'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
        'set_password': ['djoser.permissions.CurrentUserOrAdmin'],
        'username_reset': ['rest_framework.permissions.AllowAny'],
        'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
        'set_username': ['djoser.permissions.CurrentUserOrAdmin'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'user_delete': ['djoser.permissions.CurrentUserOrAdmin'],
        'user': ['djoser.permissions.CurrentUserOrAdmin'],
        'user_list': ['djoser.permissions.CurrentUserOrAdmin'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    }



.. _hide_users_setting:

HIDE_USERS
----------

.. versionadded:: 2.0

If set to True, listing ``/users/`` enpoint by normal user will return only
that user's profile in the list. Beside that, accessing ``/users/<id>/``
endpoints by user without proper permission will result in HTTP 404 instead of HTTP 403.

**Default**: ``True``
