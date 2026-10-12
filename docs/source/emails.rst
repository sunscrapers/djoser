Emails
======

Explicit email support has been removed from djoser in 1.0.0.
It didn't make sense to handle such responsibility in a package, which should
simply provide an implementation of common authentication-related REST endpoints.

Email support is now handled with the `django-templated-mail <https://github.com/sunscrapers/django-templated-mail>`_
package (2.0 or later). Each email is rendered from the ``subject``, ``text_body``
and ``html_body`` blocks of its template.

A template can extend one of djoser's and override only some blocks; the others,
and ``{{ block.super }}``, come from djoser's template:

.. code-block:: html+django

    {% extends "email/activation.html" %}

    {% block text_body %}
    {{ block.super }}
    Reply to this email if the link does not work.
    {% endblock text_body %}

Give such a template its own name and point an email class at it, since a template
cannot extend one with the same name.

Email classes can be overridden using `EMAIL setting <http://djoser.readthedocs.io/en/latest/settings.html#email>`_

If you need to customize the domain name in the email contents (fe. for user activation or password reset), see `EMAIL_FRONTEND_*` settings.
