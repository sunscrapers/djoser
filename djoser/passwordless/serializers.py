from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.conf import settings
from .utils import username_generator
from djoser.constants import Messages
from .services import PasswordlessTokenService

User = get_user_model()

# Were serializing user model to ensure the same validation and cleaning up logic defined in the model is 
# also happening in these fields. This is especially important for mobile numbers fields, which 
# can be given in a variety of formats.
class AbstractPasswordlessSignupSerializer(serializers.ModelSerializer):
    @property
    def token_request_identifier_field(self):
        raise NotImplementedError
    
    def find_user_by_identifier(self, identifier_value):
        try:
            return User.objects.get(**{self.token_request_identifier_field+'__iexact': identifier_value})
        except User.DoesNotExist:
            return None

    def validate(self, data):
        identifier_value = data[self.token_request_identifier_field]
        user = self.find_user_by_identifier(identifier_value)
        
        if not settings.PASSWORDLESS["REGISTER_NONEXISTENT_USERS"] and not user:
            raise serializers.ValidationError(Messages.CANNOT_SEND_TOKEN)
        return super().validate(data)

    def create(self, validated_data):
        identifier_value = validated_data[self.token_request_identifier_field]
        user = self.find_user_by_identifier(identifier_value)

        if settings.PASSWORDLESS["REGISTER_NONEXISTENT_USERS"] is True and not user:
            user = User.objects.create(**{
                self.token_request_identifier_field: identifier_value, 
                # In many cases, the username is mandatory
                User.USERNAME_FIELD: settings.PASSWORDLESS.USERNAME_GENERATOR(),
            })
            user.set_unusable_password()
            user.save()

        return user

class EmailPasswordlessAuthSerializer(AbstractPasswordlessSignupSerializer):
    class Meta:
        model = User
        fields = (settings.PASSWORDLESS["EMAIL_FIELD_NAME"],)
    
    @property
    def token_request_identifier_field(self):
        return settings.PASSWORDLESS["EMAIL_FIELD_NAME"]


class MobilePasswordlessAuthSerializer(AbstractPasswordlessSignupSerializer):
    class Meta:
      model = User
      fields = (settings.PASSWORDLESS["MOBILE_FIELD_NAME"],)

    @property
    def token_request_identifier_field(self):
        return settings.PASSWORDLESS["MOBILE_FIELD_NAME"]
    

# EXCHANGE (Turning a OTP into an Auth token)
# Again we're serializing the user model to ensure we get the basic validation and cleaning up
# logic (eg. standardizing phone numbers) as setup by the model fields
class PasswordlessTokenExchangeSerializer(serializers.ModelSerializer):
    
    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR
    }
        
    token = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('token',)
        if "EMAIL" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
            fields += (settings.PASSWORDLESS["EMAIL_FIELD_NAME"],)
        if "MOBILE" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
            fields += (settings.PASSWORDLESS["MOBILE_FIELD_NAME"],)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make both fields optional
        if "EMAIL" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
          self.fields[settings.PASSWORDLESS["EMAIL_FIELD_NAME"]].required = False
        if "MOBILE" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
          self.fields[settings.PASSWORDLESS["MOBILE_FIELD_NAME"]].required = False
        self.user = None

    def validate(self, attrs):
        super().validate(attrs)

        if "EMAIL" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]: 
          valid_mobile_token = PasswordlessTokenService.check_token(
              attrs.get("token", None),
              settings.PASSWORDLESS["EMAIL_FIELD_NAME"],
              attrs.get(settings.PASSWORDLESS["EMAIL_FIELD_NAME"]),
          )
        else:
          valid_mobile_token = None

        if "MOBILE" in settings.PASSWORDLESS["ALLOWED_PASSWORDLESS_METHODS"]:
          valid_email_token = PasswordlessTokenService.check_token(
              attrs.get("token", None),
              settings.PASSWORDLESS["MOBILE_FIELD_NAME"],
              attrs.get(settings.PASSWORDLESS["MOBILE_FIELD_NAME"]),
          )
        else:
          valid_email_token = None

        # WARNING - We're not checking that the user is valid, because
        # they just confirmed their email/mobile number. User will be
        # marked as active in the Action.
        print(valid_mobile_token, valid_email_token)
        valid_token = valid_mobile_token or valid_email_token
        if valid_token:
            self.user = valid_token.user
            return attrs
        
        self.fail("invalid_credentials")