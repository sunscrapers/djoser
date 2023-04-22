from templated_mail.mail import BaseEmailMessage

from djoser import utils
from djoser.conf import settings

class PasswordlessRequestEmail(BaseEmailMessage):
    template_name = "email/passwordless_request.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        if getattr(settings, "PASSWORDLESS_EMAIL_LOGIN_URL", None):
            # Eg magic links / Deep links for mobile apps
            context["url"] = settings.PASSWORDLESS["PASSWORDLESS_EMAIL_LOGIN_URL"]
        return context
