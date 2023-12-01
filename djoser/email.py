from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from djoser import utils
from djoser.conf import settings


class BaseDjoserEmail(BaseEmailMessage):
    def get_context_data(self):
        context = super().get_context_data()
        overridable = {
            "protocol": settings.EMAIL_FRONTEND_PROTOCOL,
            "domain": settings.EMAIL_FRONTEND_DOMAIN,
            "site_name": settings.EMAIL_FRONTEND_SITE_NAME,
        }
        for context_key, context_value in overridable.items():
            if context_value:
                context.update({context_key: context_value})
        return context


class ActivationEmail(BaseDjoserEmail):
    template_name = "email/activation.html"

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        return context


class ConfirmationEmail(BaseDjoserEmail):
    template_name = "email/confirmation.html"


class PasswordResetEmail(BaseDjoserEmail):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context


class PasswordChangedConfirmationEmail(BaseDjoserEmail):
    template_name = "email/password_changed_confirmation.html"


class UsernameChangedConfirmationEmail(BaseDjoserEmail):
    template_name = "email/username_changed_confirmation.html"


class UsernameResetEmail(BaseDjoserEmail):
    template_name = "email/username_reset.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.USERNAME_RESET_CONFIRM_URL.format(**context)
        return context
