import os

DEBUG = True

BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SECRET_KEY = '_'

MIDDLEWARE_CLASSES = ()

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'auth_backends.EmailAuthenticationBackend',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'testapp',
)

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
}
