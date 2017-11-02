from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class TokenStrategy:
    @classmethod
    def obtain(cls, user):
        payload = jwt_payload_handler(user)
        return {
            'token': jwt_encode_handler(payload),
            'user': user
        }
