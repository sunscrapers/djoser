Authentication Backends
=======================

Token Based Authentication
--------------------------

Add ``'rest_framework.authtoken'`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        (...),
        'rest_framework',
        'rest_framework.authtoken',
        'djoser',
        (...),
    )

Configure ``urls.py``. Pay attention to ``djoser.url.authtoken`` module path.

.. code-block:: python

    urlpatterns = patterns('',
        (...),
        url(r'^auth/', include('djoser.urls.authtoken')),
    )

Set ``TokenAuthentication`` as default Django Rest Framework authentication strategy:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
        ),
    }

Run migrations - this step will create tables for ``auth`` and ``authtoken`` apps:

.. code-block:: text

    $ ./manage.py migrate

JSON Web Token Authentication
-----------------------------

``djoser`` does not provide out of the box support for JSON web token authentication but
can be enabled by using a library like `djangorestframework-jwt <https://github.com/GetBlimp/django-rest-framework-jwt>`_.

You simply need to route correctly in your ``settings.ROOT_URLCONF``.
An example would be:

.. code-block:: python

    import rest_framework_jwt.views
    import djoser.views

    urlpatterns = [
        url(r'^auth/login', rest_framework_jwt.views.obtain_jwt_token),  # using JSON web token
        url(r'^auth/register', djoser.views.RegistrationView.as_view()),
        url(r'^auth/password/reset', djoser.views.PasswordResetView.as_view()),
        url(r'^auth/password/reset/confirm', djoser.views.PasswordResetConfirmView.as_view()),
        ...
    ]
