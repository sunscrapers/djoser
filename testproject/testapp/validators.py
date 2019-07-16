from django.core.exceptions import ValidationError


class Is666(object):
    def validate(self, password, *args, **kwargs):
        if password == "666":
            raise ValidationError("Password 666 is not allowed.", code="no666")
