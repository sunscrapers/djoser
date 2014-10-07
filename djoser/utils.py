from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from rest_framework import response, status
from . import settings


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
        return urlsafe_base64_decode(pk)
    except ImportError:
        from django.utils.http import base36_to_int
        return base36_to_int(pk)


def send_email(to_email, from_email, context, subject_template_name,
               plain_body_template_name, html_body_template_name=None):
    subject = loader.render_to_string(subject_template_name, context)
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(plain_body_template_name, context)
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_body_template_name is not None:
        html_email = loader.render_to_string(html_body_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()


class ActionViewMixin(object):

    def post(self, request):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            return self.action(serializer)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendEmailViewMixin(object):

    def send_email(self, to_email, from_email, context):
        send_email(to_email, from_email, context, **self.get_send_email_extras())

    def get_send_email_kwargs(self, user):
        return {
            'from_email': getattr(django_settings, 'DEFAULT_FROM_EMAIL', None),
            'to_email': user.email,
            'context': self.get_email_context(user),
        }

    def get_send_email_extras(self):
        raise NotImplemented

    def get_email_context(self, user):
        token = self.token_generator.make_token(user)
        uid = encode_uid(user.pk)
        return {
            'user': user,
            'domain': settings.get('DOMAIN'),
            'site_name': settings.get('SITE_NAME'),
            'uid': uid,
            'token': token,
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
