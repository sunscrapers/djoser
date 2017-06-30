Settings
========

You may optionally provide ``DJOSER`` settings:

.. code-block:: python

    DJOSER = {
        'DOMAIN': 'frontend.com',
        'SITE_NAME': 'Frontend',
        'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
        'ACTIVATION_URL': '#/activate/{uid}/{token}',
        'SEND_ACTIVATION_EMAIL': True,
        'SERIALIZERS': {},
    }

DOMAIN
------

Domain of your frontend app. If not provided, domain of current site will be
used.

**Required**: ``False``

SITE_NAME
---------

Name of your frontend app. If not provided, name of current site will be
used.

**Required**: ``False``

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
value provided by `User.get_email_field_name` is used.
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

This dictionary is used to update the defaults, so by providing,
let's say, one key, all the others will still be used.

**Examples**

.. code-block:: python

    {
        'user': 'myapp.serializers.SpecialUserSerializer',
    }

**Default**:

.. code-block:: python

    {
        'activation': 'djoser.serializers.ActivationSerializer',
        'login': 'djoser.serializers.LoginSerializer',
        'password_reset': 'djoser.serializers.PasswordResetSerializer',
        'password_reset_confirm': 'djoser.serializers.PasswordResetConfirmSerializer',
        'password_reset_confirm_retype': 'djoser.serializers.PasswordResetConfirmRetypeSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'set_password_retype': 'djoser.serializers.SetPasswordRetypeSerializer',
        'set_username': 'djoser.serializers.SetUsernameSerializer',
        'set_username_retype': 'djoser.serializers.SetUsernameRetypeSerializer',
        'user_registration': 'djoser.serializers.UserRegistrationSerializer',
        'user': 'djoser.serializers.UserSerializer',
        'token': 'djoser.serializers.TokenSerializer',
    }

USE_HTML_EMAIL_TEMPLATES
------------------------

Boolean flag which indicates whether djoser email factories should use plaintext
or HTML body templates.

+-----------------------------------+-----------------------------------+------------------------------------+
| Factory                           | Plaintext template                | HTML template                      |
+===================================+===================================+====================================+
| ``UserActivationEmailFactory``    | ``activation_email_body.txt``     | ``activation_email_body.html``     |
+-----------------------------------+-----------------------------------+------------------------------------+
| ``UserPasswordResetEmailFactory`` | ``password_reset_email_body.txt`` | ``password_reset_email_body.html`` |
+-----------------------------------+-----------------------------------+------------------------------------+
| ``UserConfirmationEmailFactory``  | ``confirmation_email_body.txt``   | ``confirmation_email_body.html``   |
+-----------------------------------+-----------------------------------+------------------------------------+
