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
