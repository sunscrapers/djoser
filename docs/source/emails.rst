Emails
======

``UserEmailFactoryBase`` which is used to send emails in djoser respects
``DEFAULT_FROM_EMAIL`` Django setting, so you can use it to customize
the default sender value.

There are few email templates which you may want to override:

* ``activation_email_body.txt``
* ``activation_email_subject.txt``
* ``password_reset_email_body.txt``
* ``password_reset_email_subject.txt``

All of them have following context:

* ``user``
* ``domain``
* ``site_name``
* ``url``
* ``uid``
* ``token``
* ``protocol``
