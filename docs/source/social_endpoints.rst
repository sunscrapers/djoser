Social Endpoints
================

.. warning::
    This API is in beta quality - backward compatibility is not guaranteed in
    future versions and you may come across bugs.

Provider Auth
-------------

Using these endpoints you can authenticate with external tools.

The workflow should look like this:

1. Access the endpoint providing a ``redirect_uri`` that would perform the
   ``POST`` action later.
2. The request would return a JSON containing one key ``authorization_url``.
   Redirect the user to that URL.
3. When the user authenticates with the external tool, that tool would redirect
   them to the ``redirect_uri`` you provided with a ``GET`` querystring
   containing two arguments: ``code`` and ``state``
4. From the view that your user got redirected to, issue a ``POST`` request
   to the endpoint with the ``code`` and ``state`` arguments. You should use
   ``application/x-www-form-urlencoded`` not JSON.  The user should be now
   authenticated in your application.
   
The list of providers is available at
`social backend docs <https://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends>`_.
please follow the instructions provided there to configure your backend.


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
