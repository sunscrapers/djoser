class TokenStrategy:
    @classmethod
    def obtain(cls, user):
        from rest_framework_jwt.settings import api_settings
        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        return {
            'token': api_settings.JWT_ENCODE_HANDLER(payload),
            'user': user
        }
