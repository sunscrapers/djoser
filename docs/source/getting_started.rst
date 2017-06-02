Getting started
===============

Installation
------------

.. code-block:: text

    $ pip install -U djoser

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

    urlpatterns = patterns('',
        (...),
        url(r'^auth/', include('djoser.urls')),
    )

HTTP Basic Auth strategy is assumed by default as Django Rest Framework does it.
However you may want to set it explicitly:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.BasicAuthentication',
        ),
    }

Run migrations - this step will create tables for ``auth`` app:

.. code-block:: text

    $ ./manage.py migrate
