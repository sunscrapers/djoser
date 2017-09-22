from django.contrib.auth.tokens import default_token_generator

from templated_mail.mail import BaseEmailMessage

from djoser import utils
from djoser.conf import settings


class ActivationEmail(BaseEmailMessage):
    template_name = 'email/activation.html'

    def set_context_data(self):
        super(ActivationEmail, self).set_context_data()

        user = self.context.get('user')
        self.context['uid'] = utils.encode_uid(user.pk)
        self.context['token'] = default_token_generator.make_token(user)
        self.context['url'] = settings.ACTIVATION_URL.format(**self.context)


class ConfirmationEmail(BaseEmailMessage):
    template_name = 'email/confirmation.html'


class PasswordResetEmail(BaseEmailMessage):
    template_name = 'email/password_reset.html'

    def set_context_data(self):
        super(PasswordResetEmail, self).set_context_data()

        user = self.context.get('user')
        self.context['uid'] = utils.encode_uid(user.pk)
        self.context['token'] = default_token_generator.make_token(user)
        self.context['url'] = settings.ACTIVATION_URL.format(**self.context)
