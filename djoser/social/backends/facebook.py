from social_core.backends.facebook import FacebookOAuth2


class FacebookOAuth2Override(FacebookOAuth2):
    REDIRECT_STATE = False
