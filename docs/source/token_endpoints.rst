Token Endpoints
===============

Token Create
------------

Use this endpoint to obtain user
`authentication token <http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication>`_.
This endpoint is available only if you are using token based authentication.

**Default URL**: ``/token/login/``

+----------+----------------------------------+----------------------------------+
| Method   | Request                          | Response                         |
+==========+==================================+==================================+
| ``POST`` | * ``{{ User.USERNAME_FIELD }}``  | ``HTTP_200_OK``                  |
|          | * ``password``                   |                                  |
|          |                                  | * ``auth_token``                 |
+----------+----------------------------------+----------------------------------+

Token Destroy
-------------

Use this endpoint to logout user (remove user authentication token).
This endpoint is available only if you are using token based authentication.

**Default URL**: ``/token/logout/``

+----------+----------------+----------------------------------+
| Method   |  Request       | Response                         |
+==========+================+==================================+
| ``POST`` | --             | ``HTTP_204_NO_CONTENT``          |
+----------+----------------+----------------------------------+
