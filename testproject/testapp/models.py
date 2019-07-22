from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self, custom_username, custom_email=None, password=None, **extra_fields
    ):
        if not custom_username:
            raise ValueError("The given custom_username must be set")
        email = self.normalize_email(custom_email)
        username = self.model.normalize_username(custom_username)
        user = self.model(custom_username=username, custom_email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    custom_username = models.CharField(max_length=150)
    custom_email = models.EmailField(blank=True)
    custom_required_field = models.CharField(max_length=2)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()

    EMAIL_FIELD = "custom_email"
    USERNAME_FIELD = "custom_username"
    REQUIRED_FIELDS = ["custom_email", "custom_required_field"]


class ExampleUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class ExampleUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = ExampleUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
