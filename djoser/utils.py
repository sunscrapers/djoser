def encode_uid(pk):
    try:
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        return urlsafe_base64_encode(force_bytes(pk))
    except ImportError:
        from django.utils.http import int_to_base36
        return int_to_base36(pk)


def decode_uid(pk):
    try:
        from django.utils.http import urlsafe_base64_decode
        return urlsafe_base64_decode(pk)
    except ImportError:
        from django.utils.http import base36_to_int
        return base36_to_int(pk)