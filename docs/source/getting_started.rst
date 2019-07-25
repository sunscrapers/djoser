Getting started
===============

Available endpoints
-------------------

* ``/users/``
* ``/users/me/``
* ``/users/confirm/``
* ``/users/resend_activation/``
* ``/users/set_password/``
* ``/users/reset_password/``
* ``/users/reset_password_confirm/``
* ``/users/set_username/``
* ``/users/reset_username/``
* ``/users/reset_username_confirm/``
* ``/token/login/`` (Token Based Authentication)
* ``/token/logout/`` (Token Based Authentication)
* ``/jwt/create/`` (JSON Web Token Authentication)
* ``/jwt/refresh/`` (JSON Web Token Authentication)
* ``/jwt/verify/`` (JSON Web Token Authentication)

Supported authentication backends
---------------------------------

* Token based authentication from `DRF <http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication>`_
* JSON Web Token authentication from `django-rest-framework-simplejwt <https://github.com/davesque/django-rest-framework-simplejwt>`_

Supported Python versions
-------------------------

* Python 3.5
* Python 3.6
* Python 3.7
* Python 3.8

Supported Django versions
-------------------------

* Django 1.11
* Django 2.2

Supported Django Rest Framework versions
----------------------------------------

* Django Rest Framework 3.9
* Django Rest Framework 3.10

Installation
------------

.. code-block:: bash

    $ pip install -U djoser

If you are going to use JWT authentication, you will also need to install
`djangorestframework_simplejwt <https://github.com/davesque/django-rest-framework-simplejwt>`_
with:

.. code-block:: bash

    $ pip install -U djangorestframework_simplejwt

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
