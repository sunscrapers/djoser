from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from djoser import utils
from djoser.conf import settings


class EmailWithUniqueLink(BaseEmailMessage):
    address = None
    
    def get_context_data(self):
        # Email can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = self.address.format(**context)
        return context


class ActivationEmail(EmailWithUniqueLink):
    template_name = "email/activation.html"
    address = settings.ACTIVATION_URL


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"


class PasswordResetEmail(EmailWithUniqueLink):
    template_name = "email/password_reset.html"
    address = settings.PASSWORD_RESET_CONFIRM_URL


class PasswordChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/password_changed_confirmation.html"


class UsernameChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/username_changed_confirmation.html"


class UsernameResetEmail(EmailWithUniqueLink):
    template_name = "email/username_reset.html"
    address = settings.USERNAME_RESET_CONFIRM_URL
