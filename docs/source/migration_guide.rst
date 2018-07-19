===============
Migration Guide
===============

-------------------------
Migrating from 1.1 to 1.2
-------------------------

There is no urgent need to change anything as backward compatibility is retained.
That being said we ask you to change usage from old endpoints to new  ones
for the warm fuzzy feeling of being more RESTful :)


-------------------------
Migrating from 0.x to 1.0
-------------------------

The stable release has introduced a number of backward incompatible changes and
purpose of this guide is to allow developer to quickly adapt a given project.

Removal of ``UserEmailFactoryBase`` and its subclasses
------------------------------------------------------

As mentioned in `Emails page <http://djoser.readthedocs.io/en/latest/emails.html>`_
since 1.0 email support has been removed from Djoser and it is advised to
use `django-templated-mail <https://github.com/sunscrapers/django-templated-mail>`_
for use cases which were previously handled by djoser email support.
You can find out more about it in the
`project documentation <http://django-templated-mail.readthedocs.io/en/latest/>`_.
Keep in mind that ``DOMAIN`` and ``SITE_NAME`` settings have also been moved to
django-templated-mail as described in
`settings page <http://django-templated-mail.readthedocs.io/en/latest/settings.html>`_.

Base URLs are no longer included with other URLs
------------------------------------------------

Previously ``djoser.urls.base`` were bundled with ``djoser.urls.authtoken``,
however in some cases developer might not need them and therefore if
base URLs are needed it is now necessary to explicitly include them, e.g.:

.. code-block:: python

    urlpatterns = [
        (...),
        url(r'^auth/', include('djoser.urls')),
        url(r'^auth/', include('djoser.urls.authtoken')),
    ]

Dropped support for Django < 1.10
---------------------------------

Support for Django 1.8 and 1.9 has been dropped in Django REST Framework 3.7
and hence there was no reason to keep it in djoser. It is recommended to upgrade
to Django 1.11, since 1.10 will EOL in December 2017.
`Django Deprecation Timeline <https://docs.djangoproject.com/en/1.11/internals/deprecation/>`_
and `Django Release Notes <https://docs.djangoproject.com/en/1.11/releases/>`_
are very helpful in the process.

Some View class names and URLs has been updated
-----------------------------------------------

Also please note that for sake of consistency all URLs now end with a trailing slash. The trailing slash is optional to ensure compatibility with frontend tools that strip the trailing slash (eg Google's Chrome browser and Angular framework).

View class names:

* ``RegistrationView`` has been renamed to ``UserCreateView``
* ``LoginView`` has been renamed to ``TokenCreateView``
* ``LogoutView`` has been renamed to ``TokenDestroyView``

Base URLs:

* ``register/`` has been renamed to ``users/create/``
* ``register`` URL name has been renamed to ``user-create``
* ``activate/`` has been renamed to ``users/activate/``
* ``activate`` URL name has been renamed to ``user-activate``

Token Based Authentication URLs:

* ``login/`` has been renamed to ``token/create/``
* ``login`` URL name has been renamed to ``token-create``
* ``logout/`` has been renamed to ``token/destroy/``
* ``logout`` URL name has been renamed to ``token-destroy``
