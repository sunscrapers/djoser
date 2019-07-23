===============
Migration Guide
===============

-------------------------
Migrating from 1.x to 2.0
-------------------------

Here are some advices to help you with the transition to new Djoser.

#. If you still use Python 2.x - stay on Djoser 1.x.
#. If you still use Django REST Framework 3.9 or lower - stay on Djoser 1.x.
#. There were several changes to default :doc:`settings<settings>`
#. User-related enpoints are gathered within UserViewSet.

-------------------------
Migrating from 1.3 to 1.4
-------------------------

Due to a lack of maintenance on the ``django-rest-framework-jwt`` project, Djoser
has switched to using ``django-rest-framework-simplejwt``. This update includes
some backwards-incompatible changes:

#. The response from the JWT Create endpoint includes both an ``access`` and
   ``refresh`` token. ``access`` is essentially the same as the old ``token`` and
   can be used to authenticate requests. ``refresh`` is used to acquire a new
   access token.
#. The JWT Refresh endpoint requires the ``refresh`` token and returns a new
   ``access`` token.
#. The JWT Verify endpoint no longer returns ``token``.
#. ``django-rest-framework-simplejwt`` uses ``Authorization: Bearer <token>``.
   This can be overridden by adding the following to Django Settings:

   .. code-block:: python

     SIMPLE_JWT = {
         'AUTH_HEADER_TYPES': ('JWT',),
     }

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

Dropped support for Django < 2.0
---------------------------------

Support for Django < 2.0 has been dropped in Djoser version 2. It is
recommended to upgrade to latest version of Django (2.2.1).

Some View class names and URLs has been updated or removed
----------------------------------------------------------

View class names:

* ``RootView`` has been removed``
* ``UserCreateView`` has been replaced to ``UserViewSet``
* ``UserDeleteView`` has been replaced to ``UserViewSet``
* ``UserView`` has been replaced to ``UserViewSet``
* ``PasswordResetView`` has been replaced to ``UserViewSet``
* ``SetPasswordView`` has been replaced to ``UserViewSet``
* ``PasswordResetConfirmView`` has been replaced to ``UserViewSet``
* ``SetUsernameView`` has been replaced to ``UserViewSet``
* ``ActivationView`` has been replaced to ``UserViewSet``
* ``ResendActivationView`` has been replaced to ``UserViewSet``

Base URLs:

* ``users/create/`` has been renamed to ``users/``
* ``users/delete/`` has been renamed to ``users/me/`` and ``users/{}/``
* ``users/confirm/`` has been renamed to ``users/activation/``
* ``users/resend/`` has been renamed to ``users/resend_activation/``
* ``password/`` has been renamed to ``users/set_password/``
* ``password/reset/`` has been renamed to ``users/reset_password/``
* ``password/reset/confirm/`` has been renamed to ``users/reset_password_confirm/``

Token Based Authentication URLs:

* ``login/`` has been renamed to ``token/create/``
* ``login`` URL name has been renamed to ``token-create``
* ``logout/`` has been renamed to ``token/destroy/``
* ``logout`` URL name has been renamed to ``token-destroy``

Added URLs:
* ``users/set_{0}/`` format(User.USERNAME_FIELD)
* ``users/reset_{0}/`` format(User.USERNAME_FIELD)
* ``users/reset_{0}_confirm/`` format(User.USERNAME_FIELD)

Dropped URLs:
* ``users/change_username/``
* ``'{0}/'.format(User.USERNAME_FIELD)``
* ``/``` RootView
