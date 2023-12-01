from django.contrib.auth.tokens import default_token_generator

from djoser import utils


class EmailContext:

    def get_context_data(self):
        context = super().get_context_data()
        context = self.add_common_context(context)
        return context
    
    def add_common_context(self, context):
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = self.url.format(**context)
        return context