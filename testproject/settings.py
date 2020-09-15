import os

DEBUG = True

BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTH_PASSWORD_VALIDATORS = [{"NAME": "testapp.validators.Is666"}]

SECRET_KEY = "_"

MIDDLEWARE = ["django.contrib.sessions.middleware.SessionMiddleware"]


INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "templated_mail",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "social_django",
    "testapp",
)

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
}

ROOT_URLCONF = "urls"

TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "djoser.social.backends.facebook.FacebookOAuth2Override",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.steam.SteamOpenId",
]

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("FACEBOOK_KEY", "")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("FACEBOOK_SECRET", "")

SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id, name, email"}

SOCIAL_AUTH_STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "")
SOCIAL_AUTH_OPENID_TRUST_ROOT = "http://test.localhost/"

DJOSER = {
    "SEND_ACTIVATION_EMAIL": False,
    "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "#/username/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": ["http://test.localhost/"],
}


SIMPLE_JWT = (
    {}
)  # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html#settings
