Settings
========

You may optionally provide ``DJOSER`` settings:

.. code-block:: python

    DJOSER = {
        'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
        'ACTIVATION_URL': '#/activate/{uid}/{token}',
        'SEND_ACTIVATION_EMAIL': True,
        'SERIALIZERS': {},
    }

PASSWORD_RESET_CONFIRM_URL
--------------------------

URL to your frontend password reset page. It should contain ``{uid}`` and
``{token}`` placeholders, e.g. ``#/password-reset/{uid}/{token}``.
You should pass ``uid`` and ``token`` to reset password confirmation endpoint.

**Required**: ``True``

SEND_ACTIVATION_EMAIL
---------------------

If ``True`` user will be required to click activation link sent in email after:

* creating an account via ``RegistrationView``
* updating his email via ``UserView``

**Default**: ``False``

SEND_CONFIRMATION_EMAIL
-----------------------

If ``True``, register or activation endpoint will send confirmation email to user.

**Default**: ``False``

ACTIVATION_URL
--------------

URL to your frontend activation page. It should contain ``{uid}`` and ``{token}``
placeholders, e.g. ``#/activate/{uid}/{token}``. You should pass ``uid`` and
``token`` to activation endpoint.

**Required**: ``True``

SET_USERNAME_RETYPE
-------------------

If ``True``, you need to pass ``re_new_{{ User.USERNAME_FIELD }}`` to
``/{{ User.USERNAME_FIELD }}/`` endpoint, to validate username equality.

**Default**: ``False``

SET_PASSWORD_RETYPE
-------------------

If ``True``, you need to pass ``re_new_password`` to ``/password/`` endpoint, to
validate password equality.

**Default**: ``False``

PASSWORD_RESET_CONFIRM_RETYPE
-----------------------------

If ``True``, you need to pass ``re_new_password`` to ``/password/reset/confirm/``
endpoint in order to validate password equality.

**Default**: ``False``

LOGOUT_ON_PASSWORD_CHANGE
-------------------------

If ``True``, setting new password will logout the user.

**Default**: ``False``

USER_EMAIL_FIELD_NAME
---------------------

Determines which field in ``User`` model is used for email in versions of Django
before 1.11. In Django 1.11 and greater value of this setting is ignored and
value provided by ``User.get_email_field_name`` is used.
This setting will be dropped when Django 1.8 LTS goes EOL.

**Default**: ``'email'``

PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
-----------------------------------

If ``True``, posting a non-existent ``email`` to ``/password/reset/`` will return
a ``HTTP_400_BAD_REQUEST`` response with an ``EMAIL_NOT_FOUND`` error message
('User with given email does not exist.').

If ``False`` (default), the ``/password/reset/`` endpoint will always return
a ``HTTP_204_NO_CONTENT`` response.

Please note that setting this to ``True`` will expose information whether
an email is registered in the system.

**Default**: ``False``

TOKEN_MODEL
-----------

Points to which token model should be used for authentication.

**Example**: ``'knox.models.AuthToken'``
**Default**: ``'rest_framework.authtoken.models.Token'``

SERIALIZERS
-----------

Dictionary which maps djoser serializer names to paths to serializer classes.
This setting provides a way to easily override given serializer(s) - it's is used
to update the defaults, so by providing, e.g. one key, all the others will stay default.

**Examples**

.. code-block:: python

    {
        'user': 'myapp.serializers.SpecialUserSerializer',
    }

**Default**:

.. code-block:: python

    {
        'activation': 'djoser.serializers.ActivationSerializer',
        'password_reset': 'djoser.serializers.PasswordResetSerializer',
        'password_reset_confirm': 'djoser.serializers.PasswordResetConfirmSerializer',
        'password_reset_confirm_retype': 'djoser.serializers.PasswordResetConfirmRetypeSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'set_password_retype': 'djoser.serializers.SetPasswordRetypeSerializer',
        'set_username': 'djoser.serializers.SetUsernameSerializer',
        'set_username_retype': 'djoser.serializers.SetUsernameRetypeSerializer',
        'user_create': 'djoser.serializers.UserCreateSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
        'user': 'djoser.serializers.UserSerializer',
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
