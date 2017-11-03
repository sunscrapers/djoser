Emails
======

Explicit email support has been removed from djoser in 1.0.0.
It didn't make sense to handle such responsibility in a package, which should
simply provide an implementation of common authentication-related REST endpoints.

Email support is now handled with the `django-templated-mail <https://github.com/sunscrapers/django-templated-mail>`_
package.

Email classes can be overridden using `EMAIL setting <http://djoser.readthedocs.io/en/latest/settings.html#email>`_
