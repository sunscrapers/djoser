import djoser.email

class ActionViewMixin(object):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)


class EmailMixin(object):
    def get_email(self):
        return djoser.email
