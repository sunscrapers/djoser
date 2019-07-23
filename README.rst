======
djoser
======

.. image:: https://img.shields.io/pypi/v/djoser.svg
   :target: https://pypi.org/project/djoser

.. image:: https://img.shields.io/travis/sunscrapers/djoser/master.svg
   :target: https://travis-ci.org/sunscrapers/djoser

.. image:: https://img.shields.io/codecov/c/github/sunscrapers/djoser.svg
   :target: https://codecov.io/gh/sunscrapers/djoser

.. image:: https://api.codacy.com/project/badge/Grade/c9bf80318d2741e5bb63912a5e0b32dc
   :alt: Codacy Badge
   :target: https://app.codacy.com/app/dekoza/djoser?utm_source=github.com&utm_medium=referral&utm_content=sunscrapers/djoser&utm_campaign=Badge_Grade_Dashboard

REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **djoser** library provides a set of `Django Rest Framework <https://www.django-rest-framework.org/>`_
views to handle basic actions such as registration, login, logout, password
reset and account activation. It works with
`custom user model <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_.

Instead of reusing Django code (e.g. ``PasswordResetForm``), we reimplemented
few things to fit better into `Single Page App <https://en.wikipedia.org/wiki/Single-page_application>`_
architecture.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

.. image:: https://asciinema.org/a/FBTYjfDPUr99jxZqbLOZhh9Pd.png
  :target: https://asciinema.org/a/FBTYjfDPUr99jxZqbLOZhh9Pd?autoplay=1&speed=2

Requirements
============

To be able to run **djoser** you have to meet following requirements:

- Python (3.5, 3.6, 3.7, 3.8)
- Django (1.11, 2.2)
- Django REST Framework (3.9, 3.10)

If you need to support other versions, please use djoser<2.

Installation
============

Simply install using ``pip``:

.. code-block:: bash

    $ pip install djoser

And continue with the steps described at
`configuration <https://djoser.readthedocs.io/en/latest/getting_started.html#configuration>`_
guide.

Documentation
=============

Documentation is available to study at
`https://djoser.readthedocs.io <https://djoser.readthedocs.io>`_
and in ``docs`` directory.

Contributing and development
============================

To start developing on **djoser**, clone the repository:

.. code-block:: bash

    $ git clone git@github.com:sunscrapers/djoser.git

If you are a **pipenv** user you can quickly setup testing environment by
using Make commands:

.. code-block:: bash

    $ make init
    $ make test

Otherwise, if you cannot use Make commands, please create virtualenv and install
requirements manually:

.. code-block:: bash

    $ pip install django djangorestframework
    $ pip install -r requirements.txt

.. code-block:: bash

    $ cd testproject
    $ ./manage.py test

If you need to run tests against all supported Python and Django versions then invoke:

.. code-block:: bash

    $ pip install tox
    $ tox -p all

You can also play with test project by running following commands:

.. code-block:: bash

    $ ./manage.py migrate
    $ ./manage.py runserver

Similar projects
================

List of projects related to Django, REST and authentication:

- `django-rest-framework-simplejwt <https://github.com/davesque/django-rest-framework-simplejwt>`_
- `django-oauth-toolkit <https://github.com/evonove/django-oauth-toolkit>`_
- `django-rest-auth <https://github.com/Tivix/django-rest-auth>`_
- `django-rest-framework-digestauth <https://github.com/juanriaza/django-rest-framework-digestauth>`_ (not maintained)
