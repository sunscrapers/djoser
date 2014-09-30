DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

SECRET_KEY = '_'

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'rest_framework',
    'rest_framework.authtoken',

    'testapp',
)

TEMPLATE_DIRS = (
    'templates',
)