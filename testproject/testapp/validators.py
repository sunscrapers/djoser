from django.core.exceptions import ValidationError


class Is666(object):
    def validate(self, password, *args, **kwargs):
        if password == '666':
            raise ValidationError("Password 666 is not allowed.", code='no666')


class Is666666(object):
    def validate(self, password, *args, **kwargs):
        if password == '666666':
            raise ValidationError("Password 666666 is extremely not allowed.", code='no666666')
