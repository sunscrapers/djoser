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

.. image:: https://img.shields.io/pypi/dm/djoser
   :target: https://img.shields.io/pypi/dm/djoser


REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **djoser** library provides a set of `Django Rest Framework <https://www.django-rest-framework.org/>`_
views to handle basic actions such as registration, login, logout, password
reset and account activation. It works with
`custom user model <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_.

Instead of reusing Django code (e.g. ``PasswordResetForm``), we reimplemented
few things to fit better into `Single Page App <https://en.wikipedia.org/wiki/Single-page_application>`_
architecture.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

.. image:: https://asciinema.org/a/94J4eG2tSBD2iEfF30a6vGtXw.png
  :target: https://asciinema.org/a/94J4eG2tSBD2iEfF30a6vGtXw

Requirements
============

To be able to run **djoser** you have to meet following requirements:

- Python (3.6, 3.7, 3.8, 3.9)
- Django (2.2, 3.1)
- Django REST Framework 3.11.1

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

We use `poetry <https://python-poetry.org/>`_ as dependency management and packaging tool.

.. code-block:: bash

    $ cd djoser
    $ poetry install -E test

This will create a virtualenv with all development dependencies.

To run the test just type:

.. code-block:: bash

    $ poetry run py.test testproject

We also preapred a convenient ``Makefile`` to automate commands above:

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

Tox
---

If you need to run tests against all supported Python and Django versions then invoke:

.. code-block:: bash

    $ poetry run tox -p all

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

    $ pre-commit install

This will ensure that your code is cleaned before you commit it.
Some steps (like black) automatically fix issues but the show their status as FAILED.
Just inspect if eveything is OK, git-add the files and retry the commit.
Other tools (like flake8) require you to manually fix the issues.


Similar projects
================

List of projects related to Django, REST and authentication:

- `django-rest-framework-simplejwt <https://github.com/davesque/django-rest-framework-simplejwt>`_
- `django-oauth-toolkit <https://github.com/evonove/django-oauth-toolkit>`_
- `django-rest-auth <https://github.com/Tivix/django-rest-auth>`_ (not maintained)
- `django-rest-framework-digestauth <https://github.com/juanriaza/django-rest-framework-digestauth>`_ (not maintained)

Please, keep in mind that while using custom authentication and TokenCreateSerializer
validation, there is a path that **ignores intentional return of None** from authenticate()
and try to find User using parameters. Probably, that will be changed in the future.
