import factory
from factory import Faker
from django.contrib.auth import get_user_model

from djoser.conf import settings as djoser_settings


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = Faker("email")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            # Check if password was explicitly passed as a parameter
            password_value = extracted if extracted is not None else "secret"
            if password_value is None:
                self.set_unusable_password()
                self.raw_password = None
            else:
                self.set_password(password_value)
                self.raw_password = password_value
            self.save()


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "testapp.CustomUser"
        skip_postgeneration_save = True

    custom_username = factory.Sequence(lambda n: f"user{n}")
    custom_email = Faker("email")
    custom_required_field = "42"

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            # Check if password was explicitly passed as a parameter
            password_value = extracted if extracted is not None else "secret"
            if password_value is None:
                self.set_unusable_password()
                self.raw_password = None
            else:
                self.set_password(password_value)
                self.raw_password = password_value
            self.save()


class ExampleUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "testapp.ExampleUser"
        skip_postgeneration_save = True

    email = Faker("email")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            # Check if password was explicitly passed as a parameter
            password_value = extracted if extracted is not None else "secret"
            if password_value is None:
                self.set_unusable_password()
                self.raw_password = None
            else:
                self.set_password(password_value)
                self.raw_password = password_value
            self.save()


class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = djoser_settings.TOKEN_MODEL

    user = factory.SubFactory(UserFactory)


class CredentialOptionsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "webauthn.CredentialOptions"

    challenge = Faker("sha256")
    username = factory.Sequence(lambda n: f"user{n}")
    display_name = Faker("name")
    ukey = Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    credential_id = Faker("sha256")
    sign_count = 0
    public_key = Faker("sha256")
