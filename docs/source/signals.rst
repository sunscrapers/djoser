Signals
=======

Djoser provides a set of `signals <https://docs.djangoproject.com/en/dev/topics/signals/>`_ that allow you to hook into Djoser user management flow.

user_registered
---------------

This signal is sent after successful user registration.

+------------+-------------------+
| Argument   | Value             |
+============+===================+
| ``sender`` | sender class      |
+------------+-------------------+
| ``user``   | user instance     |
+------------+-------------------+
| ``request``| request instance  |
+------------+-------------------+


At this point, ``user`` has already been created and saved.

user_activated
--------------

This signal is sent after successful user activation.

+------------+-------------------+
| Argument   | Value             |
+============+===================+
| ``sender`` | sender class      |
+------------+-------------------+
| ``user``   | user instance     |
+------------+-------------------+
| ``request``| request instance  |
+------------+-------------------+

At this point, ``user`` has already been activated and saved.
