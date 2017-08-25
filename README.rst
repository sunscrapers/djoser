======
djoser
======

.. image:: https://img.shields.io/pypi/v/djoser.svg
  :target: https://pypi.org/project/djoser

.. image:: https://img.shields.io/travis/sunscrapers/djoser.svg
  :target: https://travis-ci.org/sunscrapers/djoser

.. image:: https://img.shields.io/codecov/c/github/sunscrapers/djoser.svg
  :target: https://codecov.io/gh/sunscrapers/djoser

.. image:: https://img.shields.io/scrutinizer/g/sunscrapers/djoser.svg
  :target: https://scrutinizer-ci.com/g/sunscrapers/djoser

REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **djoser** library provides a set of `Django Rest Framework <http://www.django-rest-framework.org/>`_
views to handle basic actions such as registration, login, logout, password
reset and account activation. It works with `custom user model <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_.

Instead of reusing Django code (e.g. ``PasswordResetForm``), we reimplemented
few things to fit better into `Single Page App <http://en.wikipedia.org/wiki/Single-page_application)>`_
architecture.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.


Documentation
=============

Documentation is available to study at
`http://djoser.readthedocs.io <http://djoser.readthedocs.io>`_ and in
``docs`` directory.

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

If you are running djoser tests on Python 2.7 you also need to install **mock** library.

.. code-block:: bash

    $ pip install mock  # only on Python 2.7
    $ cd testproject
    $ ./manage.py test

If you need to run tests against all supported Python and Django versions then invoke:

.. code-block:: bash

    $ pip install tox
    $ tox

You can also play with test project by running following commands:

.. code-block:: bash

    $ ./manage.py migrate
    $ ./manage.py runserver

Similar projects
================

List of projects related to Django, REST and authentication:

- `django-rest-auth <https://github.com/Tivix/django-rest-auth>`_
- `django-rest-framework-digestauth <https://github.com/juanriaza/django-rest-framework-digestauth>`_
- `django-oauth-toolkit <https://github.com/evonove/django-oauth-toolkit>`_
- `doac <https://github.com/Rediker-Software/doac>`_
- `django-rest-framework-jwt <https://github.com/GetBlimp/django-rest-framework-jwt>`_
- `django-rest-framework-httpsignature <https://github.com/etoccalino/django-rest-framework-httpsignature>`_
- `hawkrest <https://github.com/kumar303/hawkrest>`_
