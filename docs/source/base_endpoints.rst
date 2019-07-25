Base Endpoints
==============

User Create
-----------

Use this endpoint to register new user. Your user model manager should
implement `create_user <https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user>`_
method and have `USERNAME_FIELD <https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD>`_
and `REQUIRED_FIELDS <https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS>`_
fields.

**Default URL**: ``/users/``

.. note::

    ``re_password`` is only required if ``USER_CREATE_PASSWORD_RETYPE`` is ``True``

+----------+-----------------------------------+----------------------------------+
| Method   |  Request                          | Response                         |
+==========+===================================+==================================+
| ``POST`` | * ``{{ User.USERNAME_FIELD }}``   | ``HTTP_201_CREATED``             |
|          | * ``{{ User.REQUIRED_FIELDS }}``  |                                  |
|          | * ``password``                    | * ``{{ User.USERNAME_FIELD }}``  |
|          | * ``re_password``                 | * ``{{ User._meta.pk.name }}``   |
|          |                                   | * ``{{ User.REQUIRED_FIELDS }}`` |
|          |                                   |                                  |
|          |                                   | ``HTTP_400_BAD_REQUEST``         |
|          |                                   |                                  |
|          |                                   | * ``{{ User.USERNAME_FIELD }}``  |
|          |                                   | * ``{{ User.REQUIRED_FIELDS }}`` |
|          |                                   | * ``password``                   |
|          |                                   | * ``re_password``                |
+----------+-----------------------------------+----------------------------------+

User Activate
-------------

Use this endpoint to activate user account. This endpoint is not a URL which
will be directly exposed to your users - you should provide site in your
frontend application (configured by ``ACTIVATION_URL``) which will send ``POST``
request to activate endpoint. ``HTTP_403_FORBIDDEN`` will be raised if user is already
active when calling this endpoint (this will happen if you call it more than once).

**Default URL**: ``/users/activation/``

+----------+--------------------------------------+----------------------------------+
| Method   | Request                              | Response                         |
+==========+======================================+==================================+
| ``POST`` | * ``uid``                            | ``HTTP_204_NO_CONTENT``          |
|          | * ``token``                          |                                  |
|          |                                      | ``HTTP_400_BAD_REQUEST``         |
|          |                                      |                                  |
|          |                                      | * ``uid``                        |
|          |                                      | * ``token``           |
|          |                                      |                                  |
|          |                                      | ``HTTP_403_FORBIDDEN``           |
|          |                                      |                                  |
|          |                                      | * ``detail``                     |
+----------+--------------------------------------+----------------------------------+

User Resend Activation E-mail
------------------------------

Use this endpoint to re-send the activation e-mail. Note that no e-mail would
be sent if the user is already active or if they don't have a usable password.
Also if the sending of activation e-mails is disabled in settings, this call
will result in ``HTTP_400_BAD_REQUEST``

**Default URL**: ``/users/resend_activation/``

+----------+--------------------------------------+----------------------------------+
| Method   | Request                              | Response                         |
+==========+======================================+==================================+
| ``POST`` | * ``{{ User.EMAIL_FIELD }}``         | ``HTTP_204_NO_CONTENT``          |
|          |                                      | ``HTTP_400_BAD_REQUEST``         |
+----------+--------------------------------------+----------------------------------+

User
----

Use this endpoint to retrieve/update the authenticated user.

**Default URL**: ``/users/me/``

+----------+--------------------------------+----------------------------------+
| Method   |           Request              |           Response               |
+==========+================================+==================================+
| ``GET``  |    --                          | ``HTTP_200_OK``                  |
|          |                                |                                  |
|          |                                | * ``{{ User.USERNAME_FIELD }}``  |
|          |                                | * ``{{ User._meta.pk.name }}``   |
|          |                                | * ``{{ User.REQUIRED_FIELDS }}`` |
+----------+--------------------------------+----------------------------------+
| ``PUT``  | ``{{ User.REQUIRED_FIELDS }}`` | ``HTTP_200_OK``                  |
|          |                                |                                  |
|          |                                | * ``{{ User.USERNAME_FIELD }}``  |
|          |                                | * ``{{ User._meta.pk.name }}``   |
|          |                                | * ``{{ User.REQUIRED_FIELDS }}`` |
|          |                                |                                  |
|          |                                | ``HTTP_400_BAD_REQUEST``         |
|          |                                |                                  |
|          |                                | * ``{{ User.REQUIRED_FIELDS }}`` |
+----------+--------------------------------+----------------------------------+
| ``PATCH``| ``{{ User.FIELDS_TO_UPDATE }}``| ``HTTP_200_OK``                  |
|          |                                |                                  |
|          |                                | * ``{{ User.USERNAME_FIELD }}``  |
|          |                                | * ``{{ User._meta.pk.name }}``   |
|          |                                | * ``{{ User.REQUIRED_FIELDS }}`` |
|          |                                |                                  |
|          |                                | ``HTTP_400_BAD_REQUEST``         |
|          |                                |                                  |
|          |                                | * ``{{ User.REQUIRED_FIELDS }}`` |
+----------+--------------------------------+----------------------------------+

User Delete
-----------

Use this endpoint to delete authenticated user. By default it will simply verify
password provided in ``current_password``, delete the auth token if token
based authentication is used and invoke delete for a given ``User`` instance.
One of ways to customize the delete behavior is to override ``User.delete``.

**Default URL**: ``/users/me/``

+------------+---------------------------------+----------------------------------+
| Method     |  Request                        | Response                         |
+============+=================================+==================================+
| ``DELETE`` | * ``current_password``          | ``HTTP_204_NO_CONTENT``          |
|            |                                 |                                  |
|            |                                 | ``HTTP_400_BAD_REQUEST``         |
|            |                                 |                                  |
|            |                                 | * ``current_password``           |
+------------+---------------------------------+----------------------------------+

Set Username
------------

Use this endpoint to change user's ``USERNAME_FIELD``.
By default this changes the ``username``.

.. note::

    URLs of following settings rely on the User model. Django allows you to set
    User.USERNAME_FIELD and User.EMAIL_FIELD fields and Djoser respects that by
    modifying its default url structure and serializers to reflect that settings.
    When you see ``{USERNAME_FIELD}`` or ``{EMAIL_FIELD}`` in the settings below,
    it means that those parts will be substituted with what you set in your User
    model.

    For example: here, the default URL is presented like this: ``/users/set_{USERNAME_FIELD}/``
    this means that if your custom User model has ``USERNAME_FIELD`` set to ``nickname``,
    the URL will look like this: ``/users/set_nickname/``. The same rule applies
    to fields sent with the request.


**Default URL**: ``/users/set_{USERNAME_FIELD}/``

.. note::

    ``re_new_{USERNAME_FIELD}`` is only required if ``SET_USERNAME_RETYPE`` is ``True``

+----------+----------------------------------------+-------------------------------------------+
| Method   | Request                                | Response                                  |
+==========+========================================+===========================================+
| ``POST`` | * ``new_{USERNAME_FIELD}``             | ``HTTP_204_NO_CONTENT``                   |
|          | * ``re_new_{USERNAME_FIELD}``          |                                           |
|          | * ``current_password``                 | ``HTTP_400_BAD_REQUEST``                  |
|          |                                        |                                           |
|          |                                        | * ``new_{USERNAME_FIELD}``                |
|          |                                        | * ``re_new_{USERNAME_FIELD}``             |
|          |                                        | * ``current_password``                    |
+----------+----------------------------------------+-------------------------------------------+

Reset Username
--------------

Use this endpoint to send email to user with username reset link. You have to
setup ``USERNAME_RESET_CONFIRM_URL``.

**Default URL**: ``/users/reset_{USERNAME_FIELD}/``

.. note::

    ``HTTP_204_NO_CONTENT`` if ``USERNAME_RESET_SHOW_EMAIL_NOT_FOUND`` is ``False``

    Otherwise if the value of ``{EMAIL_FIELD}`` does not exist in database
    ``HTTP_400_BAD_REQUEST``

+----------+---------------------------------+------------------------------+
| Method   | Request                         | Response                     |
+==========+=================================+==============================+
| ``POST`` |  ``{EMAIL_FIELD}``              | ``HTTP_204_NO_CONTENT``      |
|          |                                 |                              |
|          |                                 | ``HTTP_400_BAD_REQUEST``     |
|          |                                 |                              |
|          |                                 | * ``{EMAIL_FIELD}`` |
+----------+---------------------------------+------------------------------+

Reset Username Confirmation
---------------------------

Use this endpoint to finish reset username process. This endpoint is not a URL
which will be directly exposed to your users - you should provide site in your
frontend application (configured by ``USERNAME_RESET_CONFIRM_URL``) which
will send ``POST`` request to reset username confirmation endpoint.
``HTTP_400_BAD_REQUEST`` will be raised if the user has logged in or changed username
since the token creation.

**Default URL**: ``/users/reset_{USERNAME_FIELD}_confirm/``

.. note::

    ``re_new_username`` is only required if ``USERNAME_RESET_CONFIRM_RETYPE`` is ``True``

+----------+----------------------------------+--------------------------------------+
| Method   | Request                          | Response                             |
+==========+==================================+======================================+
| ``POST`` | * ``uid``                        | ``HTTP_204_NO_CONTENT``              |
|          | * ``token``                      |                                      |
|          | * ``new_{USERNAME_FIELD}``       | ``HTTP_400_BAD_REQUEST``             |
|          | * ``re_new_{USERNAME_FIELD}``    |                                      |
|          |                                  | * ``uid``                            |
|          |                                  | * ``token``                          |
|          |                                  | * ``new_{USERNAME_FIELD}``           |
|          |                                  | * ``re_new_{USERNAME_FIELD}``        |
+----------+----------------------------------+--------------------------------------+

Set Password
------------

Use this endpoint to change user password.

**Default URL**: ``/users/set_password/``

.. note::

    ``re_new_password`` is only required if ``SET_PASSWORD_RETYPE`` is ``True``

+----------+------------------------+-------------------------------------------+
| Method   | Request                | Response                                  |
+==========+========================+===========================================+
| ``POST`` | * ``new_password``     | ``HTTP_204_NO_CONTENT``                   |
|          | * ``re_new_password``  |                                           |
|          | * ``current_password`` | ``HTTP_400_BAD_REQUEST``                  |
|          |                        |                                           |
|          |                        | * ``new_password``                        |
|          |                        | * ``re_new_password``                     |
|          |                        | * ``current_password``                    |
+----------+------------------------+-------------------------------------------+

Reset Password
--------------

Use this endpoint to send email to user with password reset link. You have to
setup ``PASSWORD_RESET_CONFIRM_URL``.

**Default URL**: ``/users/reset_password/``

.. note::

    ``HTTP_204_NO_CONTENT`` if ``PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND`` is ``False``

    Otherwise if the value of ``{EMAIL_FIELD}`` does not exist in database
    ``HTTP_400_BAD_REQUEST``

+----------+---------------------------------+------------------------------+
| Method   | Request                         | Response                     |
+==========+=================================+==============================+
| ``POST`` |  ``{EMAIL_FIELD}``              | ``HTTP_204_NO_CONTENT``      |
|          |                                 |                              |
|          |                                 | ``HTTP_400_BAD_REQUEST``     |
|          |                                 |                              |
|          |                                 | * ``{EMAIL_FIELD}``          |
+----------+---------------------------------+------------------------------+

Reset Password Confirmation
---------------------------

Use this endpoint to finish reset password process. This endpoint is not a URL
which will be directly exposed to your users - you should provide site in your
frontend application (configured by ``PASSWORD_RESET_CONFIRM_URL``) which
will send ``POST`` request to reset password confirmation endpoint.
``HTTP_400_BAD_REQUEST`` will be raised if the user has logged in or changed password
since the token creation.

**Default URL**: ``/users/reset_password_confirm/``

.. note::

    ``re_new_password`` is only required if ``PASSWORD_RESET_CONFIRM_RETYPE`` is ``True``

+----------+----------------------------------+--------------------------------------+
| Method   | Request                          | Response                             |
+==========+==================================+======================================+
| ``POST`` | * ``uid``                        | ``HTTP_204_NO_CONTENT``              |
|          | * ``token``                      |                                      |
|          | * ``new_password``               | ``HTTP_400_BAD_REQUEST``             |
|          | * ``re_new_password``            |                                      |
|          |                                  | * ``uid``                            |
|          |                                  | * ``token``                          |
|          |                                  | * ``new_password``                   |
|          |                                  | * ``re_new_password``                |
+----------+----------------------------------+--------------------------------------+
