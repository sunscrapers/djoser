===============
Hello Pipelines
===============

Welcome to the second part of the getting started tutorial for djoser.
This part will provide you with knowledge about simple djoser pipelines and
simple customizations.

-------------
Prerequisites
-------------

- Familiarity with content covered by previous part
- http://http-prompt.com/ or https://httpie.org/ - not really required,
  because each client snippet contains http-prompt, httpie and cURL instructions,
  but these tools makes life easier.

----------------
Activation Email
----------------

By default, after new user has signed up using djoser, it will send an
confirmation email to provided email address. You may want to change this
behavior to something else, e.g. you might wish to send an activation email
instead, which would require user to follow a link to activate account to be
able to sign in.

As complicated as it may sound it's fairly simple to do in djoser.
You can achieve it with following piece of code in your settings:

.. code-block:: python

    DJOSER = {
        'ACTIVATION_URL': '#/activate/{uid}/{token}',
        'PIPELINES': {
            'user_create': [
                'djoser.pipelines.user_create.serialize_request',
                'djoser.pipelines.user_create.perform',
                'djoser.pipelines.user_create.serialize_instance',
                'djoser.pipelines.user_create.signal',
                'djoser.pipelines.email.activation_email',
            ]
        },
    }

To explain what it does we will first need to get familiar with concept of
pipelines.

----------------
Djoser Pipelines
----------------

Djoser Pipeline is essentially a list of references to functions, which may
expect some arguments. These functions are invoked one after another in
defined order. Each of these functions may return a dictionary, which is
used to extend other dictionary called context that will be used in the next
pipeline function. Pipeline context is always initialized with request.

Since examples are simpler to understand let's use the ``user_create``
pipeline, which we've been working with thus far. It is by default defined
as a following list:

.. code-block:: python

    [
        'djoser.pipelines.user_create.serialize_request',
        'djoser.pipelines.user_create.perform',
        'djoser.pipelines.user_create.serialize_instance',
        'djoser.pipelines.user_create.signal',
        'djoser.pipelines.email.confirmation_email',
    ]

As mentioned above, this list determines order of pipeline steps execution.
In case of this pipeline, during the lifetime of request ``serialize_request``
function will be called first with ``request`` argument unpacked from context.
If successful, this function returns a dictionary, which contains validated
serializer and this dictionary is then used to extend context, so the pipeline
context now contains ``request`` and ``serializer``.

Next one is ``perform``, which is responsible for creating new user with
use of ``serializer``, which has been returned in previous step. If successful,
this function returns a dictionary, which contains new user instance, so
the pipeline context now contains ``request``, ``serializer`` and ``user``.

Some pipelines provide JSON response data and ``user_create`` is one of those
pipelines and in this case ``serialize_instance`` is responsible for returning
dictionary which contains response data, so the pipeline context now contains
``request``, ``serializer``, ``user`` and ``response_data``.

Most pipelines will send a Django Signal as a way of decoupled feedback
for third party about success. In case of our example, on the ``signal``
step ``djoser.signals.user_created`` signal is sent and function doesn't
return anything, so context is left unchanged.

Finally, the ``confirmation_email`` function is responsible for sending email
to the email address provided by user. It also doesn't return anything.

Each pipeline has its own definition of steps, but some steps may be shared
among multiple pipelines e.g. ``djoser.pipelines.email.confirmation_email``
is by default contained in both ``user_create`` and ``user_activate`` pipelines.

.. note::

    As a rule of thumb - pipeline steps that do not return anything, e.g.
    signals or emails, are in general safe to remove if you don't need them.

Keep in mind that if you don't need to send email to user after sign up, you
can simply remove the email step from pipeline without consequences:

.. code-block:: python

    DJOSER = {
        'PIPELINES': {
            'user_create': [
                'djoser.pipelines.user_create.serialize_request',
                'djoser.pipelines.user_create.perform',
                'djoser.pipelines.user_create.serialize_instance',
                'djoser.pipelines.user_create.signal',
            ]
        },
    }

-------
Summary
-------

Djoser Pipelines provide us with a way to easily customize what a given API
endpoint does on request. Each piece of each pipeline can be easily replaced
and some of these can even be removed at any time.
