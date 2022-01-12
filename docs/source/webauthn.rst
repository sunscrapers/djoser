========
WebAuthn
========

`WebAuthn <https://webauthn.io/>`_ is a W3C standard for supporting registration and authorization using `U2F Token <https://en.wikipedia.org/wiki/Universal_2nd_Factor>`_. This document will focus on setting up WebAuthn with Djoser. If you wish to learn more about WebAuthn, head to `the WebAuthn guide <https://webauthn.guide/>`_.


Configuration
=============

Assuming you have Djoser installed, add ``djoser.webauthn`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        (...),
        'rest_framework',
        'djoser',
        'djoser.webauthn',
        (...),
    )


Add ``djoser.webauthn.urls`` url patterns to ``urls.py``:

.. code-block:: python

    urlpatterns = [
        (...),
        url(r'^auth/webauthn/', include('djoser.webauthn.urls')),
    ]



Endpoints
=========

Signup Request
--------------

Use this endpoint to get ``publicKey`` data for ``navigator.credentials.create``. Note that ``display_name`` is required by WebAuthn specification, but you can ignore it in your application. Unlike ``username``, ``display_name`` does not have to be unique.

**URL**: ``/signup_request/``

+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``username``                  | ``HTTP_200_OK``                  |
|          | * ``display_name``              |                                  |
|          |                                 | * ``challenge``                  |
|          |                                 | * ``rp.name``                    |
|          |                                 | * ``rp.id``                      |
|          |                                 | * ``user.id``                    |
|          |                                 | * ``user.name``                  |
|          |                                 | * ``user.displayName``           |
|          |                                 | * ``pubKeyCredParams``           |
|          |                                 | * ``timeout``                    |
|          |                                 | * ``excludeCredentials``         |
|          |                                 | * ``attestation``                |
|          |                                 | * ``extensions``                 |
|          |                                 |                                  |
|          |                                 | ``HTTP_400_BAD_REQUEST``         |
|          |                                 |                                  |
|          |                                 | * ``username``                   |
+----------+---------------------------------+----------------------------------+


Signup
------

Pass the result of ``navigator.credentials.create`` alongside user data to this endpoint in order to verify ``navigator.credentials.create`` result and create the user if verification passes.

**URL**: ``/signup/<ukey>``


+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``{{ settings.LOGIN_FIELD }}``| ``HTTP_201_CREATED``             |
|          | * ``attObj``                    |                                  |
|          | * ``clientData``                | * ``{{ settings.LOGIN_FIELD }}`` |
|          |                                 | * ``id``                         |
|          |                                 |                                  |
|          |                                 | ``HTTP_400_BAD_REQUEST``         |
|          |                                 |                                  |
|          |                                 | * ``non_field_errors``           |
|          |                                 | * ``{{ settings.LOGIN_FIELD }}`` |
+----------+---------------------------------+----------------------------------+


Login Request
-------------

Use this endpoint to get ``publicKey`` data for ``navigator.credentials.create``.


**URL**: ``/login_request/``


+----------+----------------------------------+-----------------------------------+
| Method   |           Request                |           Response                |
+==========+==================================+===================================+
| ``POST`` | * ``{{ settings.LOGIN_FIELD }}`` | ``HTTP_200_OK``                   |
|          |                                  |                                   |
|          |                                  | * ``challenge``                   |
|          |                                  | * ``allowCredentials``            |
|          |                                  | * ``rpId``                        |
|          |                                  | * ``timeout``                     |
|          |                                  |                                   |
|          |                                  | ``HTTP_400_BAD_REQUEST``          |
|          |                                  |                                   |
|          |                                  | * ``{{ settings.LOGIN_FIELD }}``  |
+----------+----------------------------------+-----------------------------------+


Login
-----

Pass the result of ``navigator.credentials.create`` alongside ``{{ settings.LOGIN_FIELD }}`` to this endpoint in order to verify ``navigator.credentials.create`` and log in the user (create the token) if verification passes.


+----------+---------------------------------+----------------------------------+
| Method   |           Request               |           Response               |
+==========+=================================+==================================+
| ``POST`` | * ``{{ settings.LOGIN_FIELD }}``| ``HTTP_201_CREATED``             |
|          | * ``signature``                 |                                  |
|          | * ``authData``                  | * ``auth_token``                 |
|          | * ``clientData``                |                                  |
|          |                                 |                                  |
|          |                                 | ``HTTP_400_BAD_REQUEST``         |
|          |                                 |                                  |
|          |                                 | * ``{{ settings.LOGIN_FIELD }}`` |
|          |                                 | * ``non_field_errors``           |
+----------+---------------------------------+----------------------------------+


Example app
===========

You can run `Test project <https://github.com/sunscrapers/djoser/tree/master/testproject>`_ to see a working example.

Running example app
-------------------

    .. code-block:: bash
    
        $ git clone git@github.com:sunscrapers/djoser.git
        $ pip install -r requirements.txt
        $ cd djoser/testproject
        $ python manage.py migrate
        $ python manage.py runserver

Navigate to ``http://localhost:8000/webauthn-example/`` and you should see a minimalistic example of using Djoser with WebAuthn. Feel free to take a look at ``testapp/static/js/webauthn.js`` file in order to better understand the whole flow.

.. note::

   ``127.0.0.1`` is not a valid `effective domain <https://html.spec.whatwg.org/multipage/origin.html#concept-origin-effective-domain>`_ and the example will not work if you navigate to ``http://127.0.0.1:8000`` instead of ``http://localhost:8000``. Also keep in mind that unless the host resolves to ``localhost``, most browsers will not allow you to use ``navigator.credentials`` if the connection is not secured with TLS.
