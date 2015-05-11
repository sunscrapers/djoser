from django.dispatch import Signal


# New user has registered.
user_registered = Signal(providing_args=["user", "request"])

# User has activated his or her account.
user_activated = Signal(providing_args=["user", "request"])
