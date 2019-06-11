class TokenStrategy:
    @classmethod
    def obtain(cls, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.utils.six import text_type

        refresh = RefreshToken.for_user(user)
        return {
            "access": text_type(refresh.access_token),
            "refresh": text_type(refresh),
            "user": user,
        }
