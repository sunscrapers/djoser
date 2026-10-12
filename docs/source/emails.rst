Emails
======

djoser sends emails for account activation, password resets and username
changes. Each one is a class built on
`django-templated-mail <https://github.com/sunscrapers/django-templated-mail>`_
(2.0 or later) and rendered from a Django template. Emails go out through your
project's ``EMAIL_BACKEND``, to the address in the user model's ``EMAIL_FIELD``.

Which emails are sent
---------------------

The names are keys of the :ref:`EMAIL setting <email-setting>`.

==================================  =============================================================  ==========================================
Name                                Sent                                                           Template
==================================  =============================================================  ==========================================
``activation``                      on registration, on ``/users/resend_activation/``, and when    ``email/activation.html``
                                    an update leaves the user inactive; only with
                                    ``SEND_ACTIVATION_EMAIL``
``confirmation``                    after activation, or on registration when activation is        ``email/confirmation.html``
                                    off; only with ``SEND_CONFIRMATION_EMAIL``
``password_reset``                  on ``/users/reset_password/``                                  ``email/password_reset.html``
``password_changed_confirmation``   after ``/users/set_password/`` and                             ``email/password_changed_confirmation.html``
                                    ``/users/reset_password_confirm/``; only with
                                    ``PASSWORD_CHANGED_EMAIL_CONFIRMATION``
``username_reset``                  on ``/users/reset_<username field>/``                          ``email/username_reset.html``
``username_changed_confirmation``   after ``/users/set_<username field>/`` and                     ``email/username_changed_confirmation.html``
                                    ``/users/reset_<username field>_confirm/``; only with
                                    ``USERNAME_CHANGED_EMAIL_CONFIRMATION``
==================================  =============================================================  ==========================================

Templates
---------

An email template defines up to three blocks: ``subject``, ``text_body`` and
``html_body``. With both bodies the email is sent as text with an HTML alternative;
with only ``html_body`` it is sent as HTML. Keep the subject on one line once it is
rendered: email headers cannot contain line breaks.

Every template gets these variables:

* ``user``: the user the email is about
* ``protocol``, ``domain`` and ``site_name``: used to build links and sign the
  email; see `Links to your frontend`_
* ``uid``, ``token`` and ``url``: only in ``activation``, ``password_reset`` and
  ``username_reset``. ``url`` is ``ACTIVATION_URL``, ``PASSWORD_RESET_CONFIRM_URL``
  or ``USERNAME_RESET_CONFIRM_URL`` with ``{uid}`` and ``{token}`` filled in.
  djoser's templates link to ``{{ protocol }}://{{ domain }}/{{ url }}``.

Links to your frontend
----------------------

``protocol``, ``domain`` and ``site_name`` are taken from the first of these that
is set:

#. djoser's :ref:`EMAIL_FRONTEND_PROTOCOL, EMAIL_FRONTEND_DOMAIN and
   EMAIL_FRONTEND_SITE_NAME <email-frontend-settings>` settings
#. the ``PROTOCOL``, ``DOMAIN`` and ``SITE_NAME`` Django settings
#. the request: the current site from ``django.contrib.sites`` if it is installed,
   otherwise the request's host, and ``https`` or ``http`` depending on whether
   the request was secure

Set the ``EMAIL_FRONTEND_*`` settings when the links should point to a frontend
on another domain than the API.

Customizing emails
------------------

Replace a template
^^^^^^^^^^^^^^^^^^

Put a template with the same name, e.g. ``email/activation.html``, in a directory
listed in ``TEMPLATES["DIRS"]``, or in an app listed before ``djoser`` in
``INSTALLED_APPS``. Django finds it before djoser's.

Extend a template
^^^^^^^^^^^^^^^^^

To change only some blocks, extend djoser's template and override those blocks.
The others, and ``{{ block.super }}``, come from djoser's template:

.. code-block:: html+django

    {# myapp/templates/myapp/email/activation.html #}
    {% extends "email/activation.html" %}

    {% block text_body %}
    {{ block.super }}
    Reply to this email if the link does not work.
    {% endblock text_body %}

A template cannot extend one with the same name, so give it its own name and use
it from an email class, as below.

Use your own email class
^^^^^^^^^^^^^^^^^^^^^^^^

Subclass one of djoser's email classes to change its template or add variables to
its context, then point the :ref:`EMAIL setting <email-setting>` at it:

.. code-block:: python

    # myapp/email.py
    from djoser import email


    class ActivationEmail(email.ActivationEmail):
        template_name = "myapp/email/activation.html"

        def get_context_data(self):
            context = super().get_context_data()
            context["support_email"] = "support@example.com"
            return context

.. code-block:: python

    # settings.py
    DJOSER = {
        "EMAIL": {
            "activation": "myapp.email.ActivationEmail",
        },
    }

The other emails keep djoser's classes; ``EMAIL`` only overrides the names it lists.
