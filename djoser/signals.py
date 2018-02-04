from django.dispatch import Signal


# User has updated password
password_updated = Signal(providing_args=['user', 'request'])

# User has reset password
password_reset_completed = Signal(providing_args=['user', 'request'])

# User has created token
token_created = Signal(providing_args=['user', 'request'])

# User has destroyed token
token_deleted = Signal(providing_args=['user', 'request'])

# New user has registered
user_created = Signal(providing_args=['user', 'request'])

# User has updated account
user_updated = Signal(providing_args=['user', 'request'])

# User has removed account
user_deleted = Signal(providing_args=['user', 'request'])

# User has activated account
user_activated = Signal(providing_args=['user', 'request'])

# User has updated username
username_updated = Signal(providing_args=['user', 'request'])
