Base Endpoints
==============

User
----

Use this endpoint to retrieve/update user.

**Default URL**: ``/me/``

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
+----------+--------------------------------+----------------------------------+

User Create
-----------

Use this endpoint to register new user. Your user model manager should
implement `create_user <https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user>`_
method and have `USERNAME_FIELD <https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD>`_
and `REQUIRED_FIELDS <https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS>`_
fields.

**Default URL**: ``/users/create/``

+----------+-----------------------------------+----------------------------------+
| Method   |  Request                          | Response                         |
+==========+===================================+==================================+
| ``POST`` | * ``{{ User.USERNAME_FIELD }}``   | ``HTTP_201_CREATED``             |
|          | * ``{{ User.REQUIRED_FIELDS }}``  |                                  |
|          | * ``password``                    | * ``{{ User.USERNAME_FIELD }}``  |
|          |                                   | * ``{{ User._meta.pk.name }}``   |
|          |                                   | * ``{{ User.REQUIRED_FIELDS }}`` |
+----------+-----------------------------------+----------------------------------+

User Delete
-----------

Use this endpoint to delete authenticated user. By default it will simply verify
password provided in ``current_password``, delete the auth token if token
based authentication is used and invoke delete for a given ``User`` instance.
One of ways to customize the delete behavior is to override ``User.delete``.

**Default URL**: ``/users/delete/``

+----------+-----------------------------------+----------------------------------+
| Method   |  Request                          | Response                         |
+==========+===================================+==================================+
| ``POST`` | * ``current_password``            | ``HTTP_204_NO_CONTENT``          |
|          |                                   |                                  |
|          |                                   | ``HTTP_400_BAD_REQUEST``         |
|          |                                   |                                  |
|          |                                   | * ``current_password``           |
+----------+-----------------------------------+----------------------------------+


User Activate
-------------

Use this endpoint to activate user account. This endpoint is not a URL which
will be directly exposed to your users - you should provide site in your
frontend application (configured by ``ACTIVATION_URL``) which will send ``POST``
request to activate endpoint.

**Default URL**: ``/users/activate/``

+----------+----------------+----------------------------------+
| Method   | Request        | Response                         |
+==========+================+==================================+
| ``POST`` | * ``uid``      | ``HTTP_204_NO_CONTENT``          |
|          | * ``token``    |                                  |
+----------+----------------+----------------------------------+

Set Username
------------

Use this endpoint to change user username (``USERNAME_FIELD``).

**Default URL**: ``/{{ User.USERNAME_FIELD }}/``

.. note::

    ``re_new_{{ User.USERNAME_FIELD }}`` is only required if ``SET_USERNAME_RETYPE`` is ``True``

+----------+----------------------------------------+--------------------------------------+
| Method   | Request                                | Response                             |
+==========+========================================+======================================+
| ``POST`` | * ``new_{{ User.USERNAME_FIELD }}``    | ``HTTP_204_NO_CONTENT``              |
|          | * ``re_new_{{ User.USERNAME_FIELD }}`` |                                      |
|          | * ``current_password``                 |                                      |
+----------+----------------------------------------+--------------------------------------+

Set Password
------------

Use this endpoint to change user password.

**Default URL**: ``/password/``

.. note::

    ``re_new_password`` is only required if ``SET_PASSWORD_RETYPE`` is ``True``

+----------+------------------------+--------------------------------------+
| Method   | Request                | Response                             |
+==========+========================+======================================+
| ``POST`` | * ``new_password``     | ``HTTP_204_NO_CONTENT``              |
|          | * ``re_new_password``  |                                      |
|          | * ``current_password`` |                                      |
+----------+------------------------+--------------------------------------+

Reset Password
--------------

Use this endpoint to send email to user with password reset link. You have to
setup ``PASSWORD_RESET_CONFIRM_URL``.

**Default URL**: ``/password/reset/``

.. note::

    ``HTTP_204_NO_CONTENT`` if ``PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND`` is ``False``

    Otherwise and if ``email`` does not exist in database ``HTTP_400_BAD_REQUEST``

+----------+-------------+-------------------------------------------------+
| Method   | Request     | Response                                        |
+==========+=============+=================================================+
| ``POST`` |  ``email``  | * ``HTTP_204_NO_CONTENT``                       |
|          |             | * ``HTTP_400_BAD_REQUEST``                      |
+----------+-------------+-------------------------------------------------+

Reset Password Confirmation
---------------------------

Use this endpoint to finish reset password process. This endpoint is not a URL
which will be directly exposed to your users - you should provide site in your
frontend application (configured by ``PASSWORD_RESET_CONFIRM_URL``) which
will send ``POST`` request to reset password confirmation endpoint.

**Default URL**: ``/password/reset/confirm/``

.. note::

    ``re_new_password`` is only required if ``PASSWORD_RESET_CONFIRM_RETYPE`` is ``True``

+----------+------------------------+--------------------------------------+
| Method   | Request                | Response                             |
+==========+========================+======================================+
| ``POST`` | * ``uid``              | ``HTTP_204_NO_CONTENT``              |
|          | * ``token``            |                                      |
|          | * ``new_password``     |                                      |
|          | * ``re_new_password``  |                                      |
+----------+------------------------+--------------------------------------+
