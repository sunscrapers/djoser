==========
Change Log
==========

This document records all notable changes to djoser.
This project adheres to `Semantic Versioning <http://semver.org/>`_.


`0.6.0`_ (2017-06-02)
---------------------

* Add ReadTheDocs integration
* Add basic `pipenv`_ integration
* Add ``Makefile`` to simplify setup and development
* Add release notes to `GitHub Releases`_ and ``CHANGELOG.rst``
* Update README with documentation split into Sphinx docs
* Update ``.travis.yml`` with approximately 3.5x faster CI builds
* Remove support for Django 1.7
* Remove support for DRF 3.3 as a consequence of dropping Django 1.7
* Slightly refactor use of ``Response`` in ``djoser/views.py``
* Fix #190 - race condition for near-simultaneous sign-ups

`0.5.4`_ (2017-01-27)
---------------------

This release adds a test case and fixes broken factory added in last release.
List of changes:

* Add ``djoser.utils.UserEmailFactoryBase`` test case
* Fix dictionary syntax error


`0.5.3`_ (2017-01-27)
---------------------

This release increases reusability of ``UserEmailFactoryBase`` in djoser / user apps.
Besides that it's mostly codebase cleanup. List of changes:

* Update ``UserEmailFactoryBase`` to accept arbitrary arguments for the context
* Update some code in ``djoser/utils.py`` to comply with PEP-8
* Update README with additional information related to djoser requirements
* Remove unnecessary requirements
* Remove leftover in ``RegistrationView`` after
  `#141 <https://github.com/sunscrapers/djoser/pull/141>`_
* Cleanup ``setup.py`` and ``testproject/testapp/tests.py``


`0.5.2`_ (2017-01-02)
---------------------

This release breaks compatibility with pre-south Django versions and adds
support for DRF 3.5. There are also some changes in documentation. List of changes:

* Add support for DRF 3.5
* Add documentation on using `djangorestframework-jwt`_ with djoser
* Update required Django version to >= 1.7
* Update docs with tweaks on encoding and names


`0.5.1`_ (2016-09-01)
---------------------

This release introduces new features controlled via appropriate setting flags.
They have been described in documentation. There also is a backward-incompatible
refactor, and other various contributions. List of changes:

* Add ``SEND_CONFIRMATION_EMAIL`` flag to djoser settings
* Add ``LOGOUT_ON_PASSWORD_CHANGE`` flag to djoser settings
* Add ``PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND`` flag to djoser settings
* Refactor ``SendEmailViewMixin`` into ```UserEmailFactoryBase``
* Update documentation
* Update user creation to wrap it inside atomic transaction
* Update ``.gitignore``
* Update tests


`0.5.0`_ (2016-06-15)
---------------------

This backward incompatible release offers a possibility to specify arbitrary
serializer for each of djoser views. It also breaks compatibility with old
Python / Django / DRF versions. List of changes:

* Add customizable serializers controlled with ``SERIALIZERS`` djoser setting field
* Update documentation
* Update ``HTTP_200_OK`` to ``HTTP_204_NO_CONTENT`` where appropriate
* Remove compatibility for Python < 2.7, Django < 1.7, and DRF < 3.3


`0.4.3`_ (2016-03-01)
---------------------

This release provides few bugfixes / UX improvements. List of changes:

* Add human readable error message when incorrect uid is provided
* Fix user being active, before activating his account via email


`0.4.2`_ (2016-02-24)
---------------------

This release adds a new feature - custom password validators. List of changes:

* Add support for ``/register/`` and ``/password/reset/confirm/`` arbitrary
  password validators, with PASSWORD_VALIDATORS djoser setting field


`0.4.1`_ (2016-02-24)
---------------------

This release adds support for new Django / Python versions. It also contains
few bugfixes / documentation updates. List of changes:

* Add check for stale activation token
* Add support for Django 1.9 and Python 3.5
* Update documentation on login and logout
* Fix `#92 <https://github.com/sunscrapers/djoser/issues/92>`_
* Fix `#100 <https://github.com/sunscrapers/djoser/pull/100>`_


`0.4.0`_ (2015-09-29)
---------------------

* Initial stable release introducing djoser as an REST implementation
  of common authentication related endpoints.
  For more information and to get started see
  `README <https://github.com/sunscrapers/djoser/blob/0.4.0/README.md>`_.


.. _pipenv: https://github.com/kennethreitz/pipenv
.. _GitHub Releases: https://github.com/sunscrapers/djoser/releases
.. _djangorestframework-jwt: https://github.com/GetBlimp/django-rest-framework-jwt
.. _0.4.0: https://github.com/sunscrapers/djoser/compare/1cf11e8...0.4.0
.. _0.4.1: https://github.com/sunscrapers/djoser/compare/0.4.0...0.4.1
.. _0.4.2: https://github.com/sunscrapers/djoser/compare/0.4.1...0.4.2
.. _0.4.3: https://github.com/sunscrapers/djoser/compare/0.4.2...0.4.3
.. _0.5.0: https://github.com/sunscrapers/djoser/compare/0.4.3...0.5.0
.. _0.5.1: https://github.com/sunscrapers/djoser/compare/0.5.0...0.5.1
.. _0.5.2: https://github.com/sunscrapers/djoser/compare/0.5.1...0.5.2
.. _0.5.3: https://github.com/sunscrapers/djoser/compare/0.5.2...0.5.3
.. _0.5.4: https://github.com/sunscrapers/djoser/compare/0.5.3...0.5.4
.. _0.6.0: https://github.com/sunscrapers/djoser/compare/0.5.4...master
