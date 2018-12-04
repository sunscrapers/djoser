Sample usage
============

We provide a standalone test app for you to start easily, see how everything works with basic settings.
It might be useful before integrating **djoser** into your backend application.

In this extremely short tutorial we are going to mimic the simplest flow:
register user, log in and log out. We will also check resource access on each consecutive step.
Let's go!

Clone repository and install **djoser** to your virtualenv:

.. code-block:: text

    $ git clone git@github.com:sunscrapers/djoser.git
    $ cd djoser
    $ pip install -e .

Go to the ``testproject`` directory, migrate the database and start the development server:

.. code-block:: text

    $ cd testproject
    $ ./manage.py migrate
    $ ./manage.py runserver 8088

Register a new user:

.. code-block:: text

    $ curl -X POST http://127.0.0.1:8088/auth/users/ --data 'username=djoser&password=alpine12'
    {"email": "", "username": "djoser", "id":1}

So far, so good. We have just created a new user using REST API.

Let's access user's details:

.. code-block:: text

    $ curl -LX GET http://127.0.0.1:8088/auth/users/me/
    {"detail": "Authentication credentials were not provided."}

As we can see, we cannot access user profile without logging in. Pretty obvious.

Let's log in:

.. code-block:: text

    curl -X POST http://127.0.0.1:8088/auth/token/login/ --data 'username=djoser&password=alpine12'
    {"auth_token": "b704c9fc3655635646356ac2950269f352ea1139"}

We have just obtained an authorization token that we may use later in order to retrieve specific resources.

Let's access user's details again:

.. code-block:: text

    $ curl -LX GET http://127.0.0.1:8088/auth/users/me/
    {"detail": "Authentication credentials were not provided."}

Access is still forbidden but let's offer the token we obtained:

.. code-block:: text

    $ curl -LX GET http://127.0.0.1:8088/auth/users/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'
    {"email": "", "username": "djoser", "id": 1}

Yay, it works!

Now let's log out:

.. code-block:: text

    curl -X POST http://127.0.0.1:8088/auth/token/logout/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'

And try access user profile again:

.. code-block:: text

    $ curl -LX GET http://127.0.0.1:8088/auth/users/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'
    {"detail": "Invalid token"}

As we can see, user has been logged out successfully and the proper token has been removed.
