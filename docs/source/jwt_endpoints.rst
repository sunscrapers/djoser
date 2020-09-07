JWT Endpoints
=============

.. note::

    Djoser settings won't have an effect on your JWT resources.
    Visit `djangorestframework-simplejwt`_  to check what can be configured.

JWT Create
----------

Use this endpoint to obtain JWT.

**Default URL**: ``/jwt/create/``

+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``{{ User.USERNAME_FIELD }}`` | ``HTTP_200_OK``                  |
|          | * ``password``                  |                                  |
|          |                                 | * ``access``                     |
|          |                                 | * ``refresh``                    |
|          |                                 |                                  |
|          |                                 | ``HTTP_401_UNAUTHORIZED``        |
|          |                                 |                                  |
|          |                                 |  * ``non_field_errors``          |
+----------+---------------------------------+----------------------------------+

JWT Refresh
-----------

Use this endpoint to refresh JWT.

**Default URL**: ``/jwt/refresh/``

+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``refresh``                   | ``HTTP_200_OK``                  |
|          |                                 |                                  |
|          |                                 | * ``access``                     |
|          |                                 |                                  |
|          |                                 | ``HTTP_401_UNAUTHORIZED``        |
|          |                                 |                                  |
|          |                                 |  * ``non_field_errors``          |
+----------+---------------------------------+----------------------------------+

JWT Verify
----------

Use this endpoint to verify JWT.

**Default URL**: ``/jwt/verify/``

+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``token``                     | ``HTTP_200_OK``                  |
|          |                                 |                                  |
|          |                                 | ``HTTP_401_UNAUTHORIZED``        |
|          |                                 |                                  |
|          |                                 |  * ``non_field_errors``          |
+----------+---------------------------------+----------------------------------+

.. _djangorestframework-simplejwt: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/
