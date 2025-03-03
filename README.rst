======
djoser
======

.. image:: https://img.shields.io/pypi/v/djoser.svg
   :target: https://pypi.org/project/djoser

.. image:: https://github.com/sunscrapers/djoser/actions/workflows/test-suite.yml/badge.svg?branch=master
    :target: https://github.com/sunscrapers/djoser/actions?query=branch%3Amaster
    :alt: Build Status

.. image:: https://codecov.io/gh/sunscrapers/djoser/branch/master/graph/badge.svg
 :target: https://codecov.io/gh/sunscrapers/djoser

.. image:: https://img.shields.io/pypi/dm/djoser
   :target: https://img.shields.io/pypi/dm/djoser

.. image:: https://readthedocs.org/projects/djoser/badge/?version=latest
    :target: https://djoser.readthedocs.io/en/latest/
    :alt: Docs

REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **djoser** library provides a set of `Django Rest Framework <https://www.django-rest-framework.org/>`_
views to handle basic actions such as registration, login, logout, password
reset and account activation. It works with
`custom user model <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_.

Supported features include:

- Token-based authentication
- JWT authentication
- Social authentication
- WebAuthn support

Instead of reusing Django code (e.g. ``PasswordResetForm``), we reimplemented
few things to fit better into `Single Page App <https://en.wikipedia.org/wiki/Single-page_application>`_
architecture.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

.. image:: https://asciinema.org/a/94J4eG2tSBD2iEfF30a6vGtXw.png
  :target: https://asciinema.org/a/94J4eG2tSBD2iEfF30a6vGtXw

Requirements
============

To be able to run **djoser** you have to meet the following requirements:

- Python>=3.9,<4.0 (including 3.10, 3.11, and 3.12)
- Django>=3.0.0 (supporting Django 3.2 through 5.1)
- Django REST Framework>=3.12

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

We use `poetry <https://python-poetry.org/>`_ as dependency management and packaging tool.

.. code-block:: bash

    $ cd djoser
    $ poetry install --all-extras

This will create a virtualenv with all development dependencies.

To run the test just type:

.. code-block:: bash

    $ poetry run pytest

We also prepared a convenient ``Makefile`` to automate commands above:

.. code-block:: bash

    $ make init
    $ make test

To activate the virtual environment run

.. code-block:: bash

    $ poetry shell

Without poetry
--------------

New versions of ``pip`` can use ``pyproject.toml`` to build the package and install its dependencies.

.. code-block:: bash

    $ pip install .[test]

.. code-block:: bash

    $ cd testproject
    $ ./manage.py test

Example project
---------------

You can also play with test project by running following commands:

.. code-block:: bash

    $ make migrate
    $ make runserver

Commiting your code
-------------------

Before sending patches please make sure you have `pre-commit <https://pre-commit.com/>`_ activated in your local git repository:

.. code-block:: bash

    $ poetry run pre-commit install

This will ensure that your code is cleaned before you commit it. The pre-commit hooks will run:

- Black (code formatting)
- Ruff (linting)
- Docformatter (docstring formatting)
- Other quality checks

Similar projects
================

List of projects related to Django, REST and authentication:

- `django-rest-registration <https://github.com/apragacz/django-rest-registration>`_
- `django-oauth-toolkit <https://github.com/evonove/django-oauth-toolkit>`_

Please, keep in mind that while using custom authentication and TokenCreateSerializer
validation, there is a path that **ignores intentional return of None** from authenticate()
and try to find User using parameters. Probably, that will be changed in the future.
