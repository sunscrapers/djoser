.. djoser documentation master file, created by
   sphinx-quickstart on Fri Jun  2 10:56:45 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======
djoser
======

.. image:: https://img.shields.io/pypi/v/djoser.svg
  :target: https://pypi.org/project/djoser

.. image:: https://img.shields.io/travis/sunscrapers/djoser/master.svg
  :target: https://travis-ci.org/sunscrapers/djoser

.. image:: https://img.shields.io/codecov/c/github/sunscrapers/djoser.svg
  :target: https://codecov.io/gh/sunscrapers/djoser

.. image:: https://img.shields.io/scrutinizer/g/sunscrapers/djoser.svg
  :target: https://scrutinizer-ci.com/g/sunscrapers/djoser

REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **djoser** library provides a set of highly customizable endpoints
built with custom solution based on
`Django Rest Framework <http://www.django-rest-framework.org/>`_
to handle basic actions related to user account.

It works with `custom user model <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_
as long as it correctly implements the ``django.contrib.auth.base_user.AbstractBaseUser``
interface.

Developed by `SUNSCRAPERS <http://sunscrapers.com/>`_ with passion & patience.

-----------------
Features In Short
-----------------

* Djoser Pipelines
* Highly Customizable
* JWT Authentication Support
* Custom User Model Support
* RESTful

Djoser works with Python 2.7 and 3.4-3.7. It is based on both Django (1.11, 2.0) and
Django REST Framework (3.7).

.. toctree::
    :maxdepth: 2
    :caption: Basics

    basics/license
    basics/installation
    basics/authentication_backends

.. toctree::
    :maxdepth: 2
    :caption: Getting Started

    getting_started/hello_request
    getting_started/hello_pipelines

.. toctree::
    :maxdepth: 2
    :caption: Settings & API

    settings
    base_endpoints
    token_endpoints
    jwt_endpoints
    social_endpoints

.. toctree::
    :maxdepth: 1
    :caption: Usage

    migration_guide
    emails
    adjustment
    examples
