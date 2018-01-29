=============
Hello Request
=============

Welcome to the first part of the getting started tutorial for djoser.
Throughout you will learn how to use, modify and expand provided
endpoints. Obviously, it doesn't cover every detail of djoser, but it will
give you solid foundation to be able to work with help of reference documentation.

-------------
Prerequisites
-------------

- Existing Django 1.11 or 2.0 project. As an alternative you can also use the
  ``basic`` example (located in ``examples/basics``). If you are not familiar
  with Django there is an excellent tutorial at https://www.djangoproject.com/start/.
- Finished :ref:`installation` guide.
- http://http-prompt.com/ or https://httpie.org/ - not really required,
  because each client snippet contains http-prompt, httpie and cURL instructions,
  but these tools makes life easier.

-----------
Simple Test
-----------

Our first task in this tutorial is to create new ``User`` instance by using
REST API provided by djoser, which you have enabled during the installation
process. It sounds quite complicated, but djoser makes it extremely simple.

Let's begin with starting the Django development server using
``./manage runserver`` or some other command you might prefer and in separate
terminal window run the following command:

.. code-block:: bash

    # http-prompt
    http-prompt 127.0.0.1:8000
    Version: 0.11.1
    http://127.0.0.1:8000> get

    # httpie
    http http://127.0.0.1:8000

    # cURL
    curl -v http://127.0.0.1:8000

    # response
    HTTP/1.1 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Length: 2
    Content-Type: application/json

    {}


This is a simple test GET request to the root of our development server.
It should result in ``200 OK`` response with empty JSON, which means that
everything works.

-----------
Create User
-----------

Now, let's try something slightly more complicated:

.. code-block:: bash

    # http-prompt
    http-prompt 127.0.0.1:8000/users/
    Version: 0.11.1
    http://127.0.0.1:8000/users/> post username="foo" password="whatever12"

    # httpie
    http POST 127.0.0.1:8000/users/ username="foo" password="whatever12"

    # cURL
    curl -v -X POST http-prompt 127.0.0.1:8000/users/ --data 'username=foo&password=whatever12'

    # response
    HTTP/1.1 201 Created
    Allow: POST, OPTIONS
    Content-Length: 25
    Content-Type: application/json

    {
        "id": 1,
        "username": "foo"
    }


In this case we've received ``201 Created`` response, which means that a new
object has been just created. We've also received some JSON, which is a
serialized representation of the user. It seems like relatively simple one,
but there is actually a lot of stuff happening backstage. First - it serializes
and validates provided data, so in case if e.g. a user with given username
already exists or if password doesn't meet requirements of
`password validation <https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_
it will return a proper error message to the client.

Actually, let's try it right now:

.. code-block:: bash

    HTTP/1.1 400 Bad Request
    Allow: POST, OPTIONS
    Content-Length: 58
    Content-Type: application/json

    {
        "username": [
            "A user with that username already exists."
        ]
    }

We've received ``400 Bad Request`` response, which means that there was a
mistake made by the client and indeed - we've provided a username, which
is already taken.

Now, that we've explained the serialization and validation stage, let's
discuss the next one, which is responsible for actually creating the user.
After this stage we're guaranteed that the new user has been created and
the transaction has been committed to database. There are rare cases, where
this stage will cause ``400 Bad Request`` response, e.g. race conditions.

Other steps are fairly simple - by default it's preparing serialized
representation of the just-created user instance, sending a signal and
sending confirmation email. We'll discuss it further in next parts of this
tutorial.

----------------
Congratulations!
----------------

You've did quite a bit of work in here - started with a simple GET request
to the root of your development server, created a new user via REST API and
learned about what's actually happening under the hood of the user create
endpoint.

Have a break and see you soon.
