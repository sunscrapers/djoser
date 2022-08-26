from templated_mail.mail import BaseEmailMessage

from djoser.conf import settings

from .email_mixins import EmailContext


class ActivationEmail(EmailContext, BaseEmailMessage):
    template_name = "email/activation.html"
    url = settings.ACTIVATION_URL


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"


class PasswordResetEmail(EmailContext, BaseEmailMessage):
    template_name = "email/password_reset.html"
    url = settings.PASSWORD_RESET_CONFIRM_URL


class PasswordChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/password_changed_confirmation.html"


class UsernameChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/username_changed_confirmation.html"


class UsernameResetEmail(EmailContext, BaseEmailMessage):
    template_name = "email/username_reset.html"
    url = settings.USERNAME_RESET_CONFIRM_URL
