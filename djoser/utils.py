from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template import loader
from rest_framework import response, status

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site


def encode_uid(pk):
    try:
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        return urlsafe_base64_encode(force_bytes(pk)).decode()
    except ImportError:
        from django.utils.http import int_to_base36
        return int_to_base36(pk)


def decode_uid(pk):
    try:
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_text
        return force_text(urlsafe_base64_decode(pk))
    except ImportError:
        from django.utils.http import base36_to_int
        return base36_to_int(pk)


def send_email(to_email, from_email, context, subject_template_name,
               plain_body_template_name=None, html_body_template_name=None):
    assert plain_body_template_name or html_body_template_name
    subject = loader.render_to_string(subject_template_name, context)
    subject = ''.join(subject.splitlines())

    if plain_body_template_name:
        plain_body = loader.render_to_string(plain_body_template_name, context)
        email_message = EmailMultiAlternatives(subject, plain_body, from_email, [to_email])
        if html_body_template_name:
            html_body = loader.render_to_string(html_body_template_name, context)
            email_message.attach_alternative(html_body, 'text/html')
    else:
        html_body = loader.render_to_string(html_body_template_name, context)
        email_message = EmailMessage(subject, html_body, from_email, [to_email])
        email_message.content_subtype = 'html'

    email_message.send()


class ActionViewMixin(object):

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return self.action(serializer)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendEmailViewMixin(object):
    token_generator = None
    subject_template_name = None
    plain_body_template_name = None
    html_body_template_name = None

    def send_email(self, to_email, from_email, context):
        send_email(to_email, from_email, context, **self.get_send_email_extras())

    def get_send_email_kwargs(self, user):
        return {
            'from_email': getattr(django_settings, 'DEFAULT_FROM_EMAIL', None),
            'to_email': user.email,
            'context': self.get_email_context(user),
        }

    def get_send_email_extras(self):
        return {
            'subject_template_name': self.get_subject_template_name(),
            'plain_body_template_name': self.get_plain_body_template_name(),
            'html_body_template_name': self.get_html_body_template_name(),
        }

    def get_subject_template_name(self):
        return self.subject_template_name

    def get_plain_body_template_name(self):
        return self.plain_body_template_name

    def get_html_body_template_name(self):
        return self.html_body_template_name

    def get_email_context(self, user):
        token = self.token_generator.make_token(user)
        uid = encode_uid(user.pk)
        try:
            domain = django_settings.DJOSER['DOMAIN']
            site_name = django_settings.DJOSER['SITE_NAME']
        except KeyError:
            site = get_current_site(self.request)
            domain, site_name = site.domain, site.name
        return {
            'user': user,
            'domain': domain,
            'site_name': site_name,
            'uid': uid,
            'token': token,
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
