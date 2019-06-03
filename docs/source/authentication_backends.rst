.. _authentication-backends:

Authentication Backends
=======================

.. note::

    Both Token Based and JWT Authentication can coexist at same time.
    Simply, follow instructions for both authentication methods and it should work.

Token Based Authentication
--------------------------

Add ``'rest_framework.authtoken'`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        (...),
        'rest_framework',
        'rest_framework.authtoken',
        'djoser',
        (...),
    ]

Configure ``urls.py``. Pay attention to ``djoser.url.authtoken`` module path:

.. code-block:: python

    urlpatterns = [
        (...),
        url(r'^auth/', include('djoser.urls')),
        url(r'^auth/', include('djoser.urls.authtoken')),
    ]

Add ``rest_framework.authentication.TokenAuthentication`` to Django REST Framework
authentication strategies tuple:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
            (...)
        ),
    }

Run migrations - this step will create tables for ``auth`` and ``authtoken`` apps:

.. code-block:: text

    $ ./manage.py migrate

JSON Web Token Authentication
-----------------------------

Django Settings
~~~~~~~~~~~~~~~

Add ``rest_framework_simplejwt.authentication.JWTAuthentication`` to
Django REST Framework authentication strategies tuple:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            (...)
        ),
    }

All settings from `django-rest-framework-simplejwt` can be configured, except for
those dealing with sliding tokens (sliding tokens are not compatible with djoser at this time):

.. code-block:: python

    SIMPLE_JWT = {
        'AUTH_HEADER_TYPES': ('JWT',),
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
        'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
        'ALGORITHM': 'HS512',
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
    }


Please see `django-rest-framework-simplejwt's docs <https://github.com/davesque/django-rest-framework-simplejwt>`_
for the detailed description of each settings. If you wish to use the blacklist functionality of
`django-rest-framework-simplejwt`, you'll need to add the `token_blacklist` to your installed apps:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        (...),
        'rest_framework',
        'djoser',
        'rest_framework_simplejwt.token_blacklist',
        (...),
    )


urls.py
~~~~~~~

Configure ``urls.py`` with ``djoser.url.jwt`` module path:

.. code-block:: python

    urlpatterns = [
        (...),
        url(r'^auth/', include('djoser.urls')),
        url(r'^auth/', include('djoser.urls.jwt')),
    ]
