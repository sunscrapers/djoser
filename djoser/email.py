from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

from djoser import utils
from django.conf import settings as django_settings
from djoser.conf import settings
from django.core import mail
from django.template.context import make_context
from django.template.loader import get_template
from django.views.generic.base import ContextMixin


class BaseEmailMessage(mail.EmailMultiAlternatives, ContextMixin):
    _node_map = {
        "subject": "subject",
        "text_body": "body",
        "html_body": "html",
    }
    template_name = None

    def __init__(self, request=None, context=None, template_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None

        if template_name is not None:
            self.template_name = template_name

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        context = dict(ctx, **self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get("domain") or (
                getattr(django_settings, "DOMAIN", "") or site.domain
            )
            protocol = context.get("protocol") or (
                "https" if self.request.is_secure() else "http"
            )
            site_name = context.get("site_name") or (
                getattr(django_settings, "SITE_NAME", "") or site.name
            )
            user = context.get("user") or self.request.user
        else:
            domain = context.get("domain") or getattr(django_settings, "DOMAIN", "")
            protocol = context.get("protocol") or "http"
            site_name = context.get("site_name") or getattr(
                django_settings, "SITE_NAME", ""
            )
            user = context.get("user")

        context.update(
            {
                "domain": domain,
                "protocol": protocol,
                "site_name": site_name,
                "user": user,
            }
        )
        return context

    def render(self):
        context = make_context(self.get_context_data(), request=self.request)
        template = get_template(self.template_name)
        with context.bind_template(template.template):
            for node in template.template.nodelist:
                self._process_node(node, context)
        self._attach_body()

    # custom interface incompatible with django, `to` is a required param
    def send(self, to, fail_silently=False, **kwargs):
        self.render()

        self.to = to
        self.cc = kwargs.pop("cc", [])
        self.bcc = kwargs.pop("bcc", [])
        self.reply_to = kwargs.pop("reply_to", [])
        self.from_email = kwargs.pop("from_email", django_settings.DEFAULT_FROM_EMAIL)
        self.request = None
        super().send(fail_silently=fail_silently)

    def _process_node(self, node, context):
        attr = self._node_map.get(getattr(node, "name", ""))
        if attr is not None:
            setattr(self, attr, node.render(context).strip())

    def _attach_body(self):
        if self.body and self.html:
            self.attach_alternative(self.html, "text/html")
        elif self.html:
            self.body = self.html
            self.content_subtype = "html"


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
        context.pop("view", None)
        return context


class ActivationEmail(BaseDjoserEmail):
    template_name = "email/activation.html"

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(getattr(user, settings.USER_ID_FIELD))
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
        context["uid"] = utils.encode_uid(getattr(user, settings.USER_ID_FIELD))
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
        context["uid"] = utils.encode_uid(getattr(user, settings.USER_ID_FIELD))
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.USERNAME_RESET_CONFIRM_URL.format(**context)
        return context
