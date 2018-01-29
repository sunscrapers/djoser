.. _installation:

============
Installation
============

This piece covers process of Djoser installation with use of various methods.

------
pipenv
------

.. code-block:: bash

    $ pipenv install djoser


Our recommendation of software to manage Python dependencies is
`pipenv <https://docs.pipenv.org/>`_. It's a wonderful tool, which solves
quite a few of time-consuming problems. If you haven't used it yet, you should
definitely give it a try.

If you are going to use JWT or third party based authentication you will also
need to install ``djangorestframework-jwt`` and ``social-auth-app-django``
respectively. You can easily install all of them with one command using:

.. code-block:: bash

    $ pipenv install djoser djangorestframework-jwt social-auth-app-django

---
pip
---

.. code-block:: bash

    $ pip install djoser


Keep in mind to create and activate a virtualenv first, using your favorite tool.
Again, if you're going to use JWT or third party based authentication you will
also need to install ``djangorestframework-jwt`` and ``social-auth-app-django``
respectively. You can easily install all of them with one command using:

.. code-block:: bash

    $ pip install djoser djangorestframework-jwt social-auth-app-django

-----------
Source Code
-----------

Full source code of djoser is always available on GitHub in
`its repository <https://github.com/sunscrapers/djoser>`_.

You can always fetch the latest version from the master branch:

.. code-block:: bash

    $ git clone git://github.com/sunscrapers/djoser.git

Or the latest tarball:

.. code-block:: bash

    $ curl -OL https://github.com/sunscrapers/djoser/tarball/master

-------------
Configuration
-------------

Add ``'djoser'`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        ...,
        'rest_framework',
        'djoser',
        ...,
    )

Add ``'djoser.urls.base'`` patterns include to your ``urlpatterns``:

.. code-block:: python

    urlpatterns = [
        ...,
        url(r'^', include('djoser.urls.base')),
    ]

If you are using Django 2.0 you can also use the new routing:

.. code-block:: python

    urlpatterns = [
        ...,
        path('', include('djoser.urls.base')),
    ]

HTTP Basic Auth strategy is assumed by default as Django REST Framework does it.
We strongly encourage you to consider other authentication method described in
:ref:`authentication-backends`.

In case of third party based authentication
`PSA backend docs <https://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends>`_
will be a great reference to configure given provider.

------
Verify
------

To verify that you have installed djoser properly you can try a simple test
using your **django** shell. Start it with ``./manage.py shell`` and inside
the prompt try the following code:

.. code-block:: python

    from django.urls import resolvers
    urls = resolvers.get_resolver()
    print(urls.url_patterns)

You are ready to move on if your result contains something similar to this:

.. code-block:: python

    <URLResolver <module 'djoser.urls.base' ...> (None:None) ''>]
