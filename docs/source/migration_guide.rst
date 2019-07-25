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


Some View class names and URLs has been updated or removed
----------------------------------------------------------

View class names:

* ``RootView`` has been removed
* ``UserCreateView``, ``UserDeleteView``, ``UserView``, ``PasswordResetView``,
``SetPasswordView``,  ``PasswordResetConfirmView``, ``SetUsernameView``,
``ActivationView``, and ``ResendActivationView`` have all been removed
and replaced by appropriate sub-views within ``UserViewSet``.

If you subclassed any of those views, you need to refactor your code - we suggest
subclassing UserViewSet and overwrite appropriate methods there.

Base URLs:

* ``users/create/``, ``users/delete/``, ``users/confirm/``, and ``users/resend/``
  removed; use viewset-provided enpoints (see :doc:`settings<settings>`)
* ``password/`` has been renamed to ``users/set_password/``
* ``password/reset/`` has been renamed to ``users/reset_password/``
* ``password/reset/confirm/`` has been renamed to ``users/reset_password_confirm/``

Token Based Authentication URLs:

* use ``token/login`` to create token
* user ``token/logout`` to invalidate the token

Added URLs:
* ``users/set_{0}/`` format(User.USERNAME_FIELD)
* ``users/reset_{0}/`` format(User.USERNAME_FIELD)
* ``users/reset_{0}_confirm/`` format(User.USERNAME_FIELD)

If anything else stopped working: consult :doc:`settings<settings>` first before
filing a bug report.
