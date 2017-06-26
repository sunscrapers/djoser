try:
    from django.contrib.auth.password_validation import validate_password
except ImportError:
    from password_validation import validate_password
