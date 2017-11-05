Social Endpoints
================

.. warning::
    This API is in beta quality - backward compatibility is not guaranteed in
    future versions and you may come across bugs.

Provider Auth
-------------

Use this endpoint to obtain authorization URL for a given provider with the
GET method or to obtain authentication token with POST method. List of providers
is available at
`social backend docs <https://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends>`_.

**Default URL**: ``/o/{{ provider }}/``

.. note::
    * ``redirect_uri`` is provided via GET parameters - not JSON
    * ``state`` parameter isn't always required e.g. in case of OpenID backends

+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``GET``  | * ``redirect_uri``              | ``HTTP_200_OK``                  |
|          |                                 |                                  |
|          |                                 | * ``authorization_url``          |
|          |                                 |                                  |
|          |                                 | ``HTTP_400_BAD_REQUEST``         |
+----------+---------------------------------+----------------------------------+
| ``POST`` | * ``code``                      | ``HTTP_201_CREATED``             |
|          | * ``state``                     |                                  |
|          |                                 | * ``token``                      |
|          |                                 |                                  |
|          |                                 | ``HTTP_400_BAD_REQUEST``         |
|          |                                 |                                  |
|          |                                 |  * ``non_field_errors``          |
+----------+---------------------------------+----------------------------------+
