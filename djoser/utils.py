from django.conf import settings as django_settings
from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import loader
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from djoser import constants
from djoser.compat import get_user_email
from djoser.conf import settings


def encode_uid(pk):
    return urlsafe_base64_encode(force_bytes(pk)).decode()


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


def login_user(request, user):
    token, _ = settings.TOKEN_MODEL.objects.get_or_create(user=user)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def logout_user(request):
    settings.TOKEN_MODEL.objects.filter(user=request.user).delete()
    user_logged_out.send(
        sender=request.user.__class__, request=request, user=request.user
    )


def send_email(request, factory, user):
    email_factory = factory.from_request(request, user)
    email = email_factory.create()
    email.send()


class ActionViewMixin(object):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)


class UserEmailFactoryBase(object):
    token_generator = default_token_generator
    subject_template_name = None
    plain_body_template_name = None
    html_body_template_name = None

    def __init__(self, from_email, user, protocol, domain, site_name,
                 **context_data):
        self.from_email = from_email
        self.user = user
        self.domain = domain
        self.site_name = site_name
        self.protocol = protocol
        self.context_data = context_data

    @classmethod
    def from_request(cls, request, user=None, from_email=None, protocol=None,
                     **context_data):
        site = get_current_site(request)
        from_email = from_email or getattr(
            django_settings, 'DEFAULT_FROM_EMAIL', ''
        )

        return cls(
            from_email=from_email,
            user=user or request.user,
            domain=django_settings.DJOSER.get('DOMAIN') or site.domain,
            site_name=django_settings.DJOSER.get('SITE_NAME') or site.name,
            protocol=protocol or ('https' if request.is_secure() else 'http'),
            **context_data
        )

    def create(self):
        assert self.plain_body_template_name or self.html_body_template_name
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        user_email = get_user_email(self.user)
        if user_email is None:
            raise ValueError(constants.USER_WITHOUT_EMAIL_FIELD_ERROR)

        if self.plain_body_template_name:
            plain_body = loader.render_to_string(
                self.plain_body_template_name, context
            )
            email_message = EmailMultiAlternatives(
                subject, plain_body, self.from_email, [user_email]
            )
            if self.html_body_template_name:
                html_body = loader.render_to_string(
                    self.html_body_template_name, context
                )
                email_message.attach_alternative(html_body, 'text/html')
        else:
            html_body = loader.render_to_string(
                self.html_body_template_name, context
            )
            email_message = EmailMessage(
                subject, html_body, self.from_email, [user_email]
            )
            email_message.content_subtype = 'html'
        return email_message

    def get_context(self):
        context = {
            'user': self.user,
            'domain': self.domain,
            'site_name': self.site_name,
            'uid': encode_uid(self.user.pk),
            'token': self.token_generator.make_token(self.user),
            'protocol': self.protocol,
        }
        context.update(self.context_data)
        return context


class UserActivationEmailFactory(UserEmailFactoryBase):
    subject_template_name = 'activation_email_subject.txt'
    plain_body_template_name = 'activation_email_body.txt'
    if settings.USE_HTML_EMAIL_TEMPLATES:
        html_body_template_name = 'activation_email_body.html'

    def get_context(self):
        context = super(UserActivationEmailFactory, self).get_context()
        context['url'] = settings.ACTIVATION_URL.format(**context)
        return context


class UserPasswordResetEmailFactory(UserEmailFactoryBase):
    subject_template_name = 'password_reset_email_subject.txt'
    plain_body_template_name = 'password_reset_email_body.txt'
    if settings.USE_HTML_EMAIL_TEMPLATES:
        html_body_template_name = 'password_reset_email_body.html'

    def get_context(self):
        context = super(UserPasswordResetEmailFactory, self).get_context()
        context['url'] = settings.PASSWORD_RESET_CONFIRM_URL.format(
            **context
        )
        return context


class UserConfirmationEmailFactory(UserEmailFactoryBase):
    subject_template_name = 'confirmation_email_subject.txt'
    plain_body_template_name = 'confirmation_email_body.txt'
    if settings.USE_HTML_EMAIL_TEMPLATES:
        html_body_template_name = 'confirmation_email_body.html'
