class UserLookupConverter:
    """
    Matches a user lookup value, excluding dots.

    Mirrors the regex DRF's SimpleRouter used before the URLs were written by hand.
    Excluding dots is what keeps ``/users/1.json`` routable as a format suffix rather
    than being swallowed as a lookup value of ``"1.json"``.
    """

    regex = r"[^/.]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return str(value)
