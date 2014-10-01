from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send(to_email,
         from_email,
         context,
         subject_template_name,
         plain_body_template_name,
         html_body_template_name=None):
    subject = loader.render_to_string(subject_template_name, context)
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(plain_body_template_name, context)
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_body_template_name is not None:
        html_email = loader.render_to_string(html_body_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()