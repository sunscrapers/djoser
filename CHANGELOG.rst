==========
Change Log
==========

This document records all notable changes to djoser.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

---------------------
`2.0.5`_ (2020-09-03)
---------------------

* fix readme formatting on pypi

---------------------
`2.0.4`_ (2020-09-03)
---------------------

* add official support for Django 3.x
* resolve all Django 4.x warnings

---------------------
`2.0.3`_ (2019-08-24)
---------------------

* Fixed login validation

---------------------
`2.0.2`_ (2019-08-17)
---------------------

* Fixed sending email after activation
* Fix user deletion serializer and permission class

---------------------
`2.0.1`_ (2019-07-25)
---------------------

* Fixed a registration bug when ``USER_CREATE_PASSWORD_RETYPE`` is set to ``True``.

---------------------
`2.0.0`_ (2019-07-23)
---------------------

* Drop support for Python<3.5
* Drop support for djangorestframework<3.10
* Drop legacy routes
* Reworked permissions logic and default classes (see :ref:`View Permission Settings<view-permission-settings>`)
* Add ``CONSTANTS`` option to settings (@mrouhi13)
* Remove deprecated ``CurrentUserSerializer``
* Remove deprecated ``settings.get()`` method

---------------------
`1.7.0`_ (2019-05-25)
---------------------

* Add LOGIN_FIELD setting
* Add CONSTANTS option to settings (@mrouhi13)
* Add USER_CREATE_PASSWORD_RETYPE option (@Chadys)
* Allow using custom email field (@Chadys)
* Remove non_field_error from base endpoints (@Chadys)
* Other small fixes

---------------------
`1.6.0`_ (2019-05-15)
---------------------

* Added Russian translation (@ozeranskiy)
* Added French translation (@Chadys)
* Fix superfluous translation string (@Chadys)
* Prevent non-staff users from getting other users' data (@hawi74)
* Fix tests for Python 2.7
* Fix some problems in documentation

---------------------
`1.5.1`_ (2019-04-02)
---------------------

* Fixed a vulnerability of UserViewSet that allowed to create new accounts on wrong endpoint. (Thanks to @karazuba for reporting)
* Past minor version since 1.2 will get a bugfix update and affected versions will be removed from PyPI to prevent affected versions from being installed.

---------------------
`1.5.0`_ (2019-03-05)
---------------------

* Added endpoint to resend activation email.
* Added Polish and Georgian translations.
* Fix missing **kwargs in ActionViewmixin.post() handler.
* Fixed documentation.
* Other small fixes.

---------------------
`1.4.0`_ (2019-01-09)
---------------------

* Introduced new framework for setting default permissions for certain views.
  See :ref:`documentation<view-permission-settings>`.
* Fix permissions regression introduced in 1.3.2.
  Default permission for user-list view set to read-only, like in 1.3.2
  (defaults to read-only like in 1.3.2).

---------------------
`1.3.2`_ (2018-12-05)
---------------------

* Fix vulnerability of user endpoints.
* Fix issue  that appears on DRF 3.9+ on legacy `/me/` endpoint.

---------------------
`1.3.1`_ (2018-10-09)
---------------------

* Fix issue with circular import

---------------------
`1.3.0`_ (2018-09-12)
---------------------

* Split user serializers (thanks to @joshua-s)
* Add Django 2.1 to tox.ini
* Update travis.yml

---------------------
`1.2.0`_ (2018-07-23)
---------------------

* Refactor urls to use new RESTful ViewSets
* Retain old urls for compatibility
* Add Django 2.0 to tox.ini
* Add DRF 3.8 to tox.ini
* Drop Django 1.10 support
* Update requirements.txt
* Update travis.yml
* Update .gitignore

---------------------
`1.1.5`_ (2017-12-08)
---------------------

* Add Steam config to testproject
* Add python egg data to .gitignore
* Update social auth serializer to use GET parameters instead of JSON data
* Update python-social-auth integration tests to use GET parameters
* Update social auth credentials in testproject to use environment variables by default

---------------------
`1.1.4`_ (2017-11-22)
---------------------

* Add proper validation errors for OAuth state validation

---------------------
`1.1.3`_ (2017-11-22)
---------------------

* Update python-social-auth load strategy invoke to use proper requests

---------------------
`1.1.2`_ (2017-11-22)
---------------------

* Fix: Request data is not available in python-social-auth backends

---------------------
`1.1.1`_ (2017-11-05)
---------------------

* Fix: Token Strategy breaks in all cases if djangorestframework-jwt not installed

---------------------
`1.1.0`_ (2017-11-05)
---------------------

* Add third party based authentication support
* Add JWT token strategy for new authentication method
* Add ``EMAIL`` setting to allow simpler email customization.
* Add ``SOCIAL_AUTH_TOKEN_STRATEGY`` and ``SOCIAL_AUTH_ALLOWED_REDIRECT_URIS``
  settings along new authentication method
* Add documentation about new authentication method
* Update documentation index into captioned sections for better readability


---------------------
`1.0.1`_ (2017-10-20)
---------------------

* Fix: Invalid URL for PasswordResetEmail context
* Fix: Invalid serializer examples in docs

---------------------
`1.0.0`_ (2017-10-14)
---------------------

* **Breaking**: For Token-based and JWT authentication ``djoser.urls`` should be included in the URLconf as well as either ``djoser.urls.authtoken`` or ``djoser.urls.jwt``
* Add JWT authentication support
* Add/Update documentation about JWT
* Add/Update/Fix tests where necessary
* Add support for Django REST Framework 3.7
* Drop support for Django REST Framework 3.6
* Replace built-in email support with django-templated-mail
* Refactor test configuration for better performance and organization
* Refactor RootView to have better support for modular URLs
* Update URLs to be slightly more RESTful
* Update codebase with small syntax/formatting fixes
* Update README/documentation to reflect on codebase changes
* Move ``DOMAIN`` and ``SITE_NAME`` settings to django-templated-mail
* Remove ``USE_HTML_EMAIL_TEMPLATES`` and ``ROOT_VIEW_URLS_MAPPING`` settings

---------------------
`0.7.0`_ (2017-09-01)
---------------------

* Add ``TOKEN_MODEL`` setting to allow third party apps to specify a custom token model
* Add ``USER_EMAIL_FIELD_NAME`` setting as a compatibility solution in Django < 1.11
* Add support for Django Password Validators
* Add HTML templates for djoser emails
* Add `flake8`_ integration to CI
* Add `py.test`_ integration
* Add Python 3.7 to CI
* Update from coveralls to codecov
* Update ``README`` to rST with uniform badges
* Update ``djoser.views.PasswordResetView`` to allow non-database ``User.is_active``
* Update docs on topics which have been added/modified since last release
* Remove serializers manager, so the serializers in djoser are now accessed via dot notation
* Remove support for DRF 3.4
* Remove support for basic auth as authentication backend
* Refactor djoser settings module for cleaner and more pythonic/djangonic solution
* Refactor tests into multiple files and fix some minor issues
* Refactor some parts of codebase for better readability
* Slightly refactor/simplify parts of ``djoser.utils``
* Fix all style issues reported by `flake8`_ in codebase
* Fix security bug in ``djoser.views.UserView``

---------------------
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

---------------------
`0.5.4`_ (2017-01-27)
---------------------

This release adds a test case and fixes broken factory added in last release.
List of changes:

* Add ``djoser.utils.UserEmailFactoryBase`` test case
* Fix dictionary syntax error

---------------------
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

---------------------
`0.5.2`_ (2017-01-02)
---------------------

This release breaks compatibility with pre-south Django versions and adds
support for DRF 3.5. There are also some changes in documentation. List of changes:

* Add support for DRF 3.5
* Add documentation on using `djangorestframework-jwt`_ with djoser
* Update required Django version to >= 1.7
* Update docs with tweaks on encoding and names

---------------------
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

---------------------
`0.5.0`_ (2016-06-15)
---------------------

This backward incompatible release offers a possibility to specify arbitrary
serializer for each of djoser views. It also breaks compatibility with old
Python / Django / DRF versions. List of changes:

* Add customizable serializers controlled with ``SERIALIZERS`` djoser setting field
* Update documentation
* Update ``HTTP_200_OK`` to ``HTTP_204_NO_CONTENT`` where appropriate
* Remove compatibility for Python < 2.7, Django < 1.7, and DRF < 3.3

---------------------
`0.4.3`_ (2016-03-01)
---------------------

This release provides few bugfixes / UX improvements. List of changes:

* Add human readable error message when incorrect uid is provided
* Fix user being active, before activating his account via email

---------------------
`0.4.2`_ (2016-02-24)
---------------------

This release adds a new feature - custom password validators. List of changes:

* Add support for ``/register/`` and ``/password/reset/confirm/`` arbitrary
  password validators, with PASSWORD_VALIDATORS djoser setting field

---------------------
`0.4.1`_ (2016-02-24)
---------------------

This release adds support for new Django / Python versions. It also contains
few bugfixes / documentation updates. List of changes:

* Add check for stale activation token
* Add support for Django 1.9 and Python 3.5
* Update documentation on login and logout
* Fix `#92 <https://github.com/sunscrapers/djoser/issues/92>`_
* Fix `#100 <https://github.com/sunscrapers/djoser/pull/100>`_

---------------------
`0.4.0`_ (2015-09-29)
---------------------

* Initial stable release introducing djoser as an REST implementation
  of common authentication related endpoints.
  For more information and to get started see
  `README <https://github.com/sunscrapers/djoser/blob/0.4.0/README.md>`_.


.. _pipenv: https://github.com/kennethreitz/pipenv
.. _flake8: http://flake8.pycqa.org
.. _py.test: https://pytest.org/
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
.. _0.6.0: https://github.com/sunscrapers/djoser/compare/0.5.4...0.6.0
.. _0.7.0: https://github.com/sunscrapers/djoser/compare/0.6.0...0.7.0
.. _1.0.0: https://github.com/sunscrapers/djoser/compare/0.6.0...1.0.0
.. _1.0.1: https://github.com/sunscrapers/djoser/compare/1.0.0...1.0.1
.. _1.1.0: https://github.com/sunscrapers/djoser/compare/1.0.1...1.1.0
.. _1.1.1: https://github.com/sunscrapers/djoser/compare/1.1.0...1.1.1
.. _1.1.2: https://github.com/sunscrapers/djoser/compare/1.1.1...1.1.2
.. _1.1.3: https://github.com/sunscrapers/djoser/compare/1.1.2...1.1.3
.. _1.1.4: https://github.com/sunscrapers/djoser/compare/1.1.3...1.1.4
.. _1.1.5: https://github.com/sunscrapers/djoser/compare/1.1.4...1.1.5
.. _1.2.0: https://github.com/sunscrapers/djoser/compare/1.1.5...1.2.0
.. _1.3.0: https://github.com/sunscrapers/djoser/compare/1.2.0...1.3.0
.. _1.3.1: https://github.com/sunscrapers/djoser/compare/1.3.0...1.3.1
.. _1.3.2: https://github.com/sunscrapers/djoser/compare/1.3.1...1.3.2
.. _1.3.3: https://github.com/sunscrapers/djoser/compare/1.3.2...1.3.3
.. _1.4.0: https://github.com/sunscrapers/djoser/compare/1.3.3...1.4.0
.. _1.5.0: https://github.com/sunscrapers/djoser/compare/1.4.0...1.5.0
.. _1.5.1: https://github.com/sunscrapers/djoser/compare/1.5.0...1.5.1
.. _1.6.0: https://github.com/sunscrapers/djoser/compare/1.5.1...1.6.0
.. _1.7.0: https://github.com/sunscrapers/djoser/compare/1.6.0...1.7.0
.. _2.0.0: https://github.com/sunscrapers/djoser/compare/1.7.0...2.0.0
.. _2.0.1: https://github.com/sunscrapers/djoser/compare/2.0.0...2.0.1
.. _2.0.2: https://github.com/sunscrapers/djoser/compare/2.0.1...2.0.2
.. _2.0.3: https://github.com/sunscrapers/djoser/compare/2.0.2...2.0.3
.. _2.0.4: https://github.com/sunscrapers/djoser/compare/2.0.3...2.0.4
.. _2.0.5: https://github.com/sunscrapers/djoser/compare/2.0.4...2.0.5
