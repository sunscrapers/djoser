Getting started
===============

Available endpoints
-------------------

* ``/me/``
* ``/users/create/``
* ``/users/delete/``
* ``/users/activate/``
* ``/{{ User.USERNAME_FIELD }}/``
* ``/password/``
* ``/password/reset/``
* ``/password/reset/confirm/``
* ``/token/create/`` (Token Based Authentication)
* ``/token/destroy/`` (Token Based Authentication)
* ``/jwt/create/`` (JSON Web Token Authentication)
* ``/jwt/refresh/`` (JSON Web Token Authentication)
* ``/jwt/verify/`` (JSON Web Token Authentication)

Supported authentication backends
---------------------------------

* Token based authentication from `DRF <http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication>`_
* JSON Web Token authentication from `django-rest-framework-jwt <https://github.com/GetBlimp/django-rest-framework-jwt>`_

Supported Python versions
-------------------------

* Python 2.7
* Python 3.4
* Python 3.5
* Python 3.6

Supported Django versions
-------------------------

* Django 1.10
* Django 1.11

Supported Django Rest Framework versions
----------------------------------------

* Django Rest Framework 3.7

Installation
------------

.. code-block:: bash

    $ pip install -U djoser

If you are going to use JWT authentication, you will also need to install
`djangorestframework-jwt <https://github.com/GetBlimp/django-rest-framework-jwt>`_
with:

.. code-block:: bash

    $ pip install -U djangorestframework-jwt

Finally if you are going to use third party based authentication e.g. facebook,
you will need to install `social-auth-app-django <https://github.com/python-social-auth/social-app-django>`_
with:

.. code-block:: bash

    $ pip install -U social-auth-app-django

Configuration
-------------

Configure ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        (...),
        'rest_framework',
        'djoser',
        (...),
    )

Configure ``urls.py``:

.. code-block:: python

    urlpatterns = [
        (...),
        url(r'^auth/', include('djoser.urls')),
    ]

HTTP Basic Auth strategy is assumed by default as Django Rest Framework does it.
We strongly discourage and do not provide any explicit support for basic auth.
You should customize your authentication backend as described in
:ref:`authentication-backends`.

In case of third party based authentication
`PSA backend docs <https://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends>`_
will be a great reference to configure given provider.
