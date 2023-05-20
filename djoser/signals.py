from django.dispatch import Signal

# New user has registered. Args: user, request.
user_registered = Signal()

# User has activated his or her account. Args: user, request.
user_activated = Signal()

# User has been updated. Args: user, request.
user_updated = Signal()
