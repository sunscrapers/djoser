# djoser

[![Build Status](https://travis-ci.org/sunscrapers/djoser.svg?branch=master)](https://travis-ci.org/sunscrapers/djoser)
[![Coverage Status](https://coveralls.io/repos/sunscrapers/djoser/badge.png?branch=master)](https://coveralls.io/r/sunscrapers/djoser?branch=master)

REST implementation of [Django](https://www.djangoproject.com/) authentication
system. **Djoser** library provides a set of [Django Rest Framework](http://www.django-rest-framework.org/)
views to handle basic actions such as registration, login, logout, password
reset and account activation. It works with [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/).

Instead of reusing Django code (e.g. `PasswordResetForm`), we reimplemented
few things to fit better into [Single Page App](http://en.wikipedia.org/wiki/Single-page_application)
architecture.

Developed by [SUNSCRAPERS](http://sunscrapers.com/) with passion & patience.

## Features

Here is a list of supported authentication backends:

 * [HTTP Basic Auth](http://www.django-rest-framework.org/api-guide/authentication/#basicauthentication) (Default)
 * [Token based authentication from Django Rest Framework](http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication)

Available endpoints:

 * `/me/`
 * `/register/`
 * `/login/` (token based authentication)
 * `/logout/` (token based authentication)
 * `/activate/`
 * `/{{ User.USERNAME_FIELD }}/`
 * `/password/`
 * `/password/reset/`
 * `/password/reset/confirm/`

Supported Python versions:

 * Python 2.6
 * Python 2.7
 * Python 3.4
 * Python 3.5

Supported Django versions:

 * Django 1.5
 * Django 1.6
 * Django 1.7
 * Django 1.8

Supported Django Rest Framework versions:

 * Django Rest Framework 3.x
 
For Django Rest Framework 2.4 support check [djoser 0.3.2](https://github.com/sunscrapers/djoser/tree/0.3.2). 

## Installation

Use `pip`:

    $ pip install djoser

## Quick Start

Configure `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    (...),
    'rest_framework',
    'djoser',
    (...),
)
```

Configure `urls.py`:

```python
urlpatterns = patterns('',
    (...),
    url(r'^auth/', include('djoser.urls')),
)
```

HTTP Basic Auth strategy is assumed by default as Django Rest Framework does it. However you may want to set it
explicitly:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    ),
}
```

Run migrations (if you are using Django 1.7+ or South) - this step will create tables for `auth` app:

    $ ./manage.py migrate

## Customizing authentication backend

### Token Based Authentication

Add `'rest_framework.authtoken'` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    (...),
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    (...),
)
```

Configure `urls.py`. Pay attention to `djoser.url.authtoken` module path.

```python
urlpatterns = patterns('',
    (...),
    url(r'^auth/', include('djoser.urls.authtoken')),
)
```

Set `TokenAuthentication` as default Django Rest Framework authentication strategy:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}
```

Run migrations (if you are using Django 1.7+ or South) - this step will create tables for `auth` and `authtoken` apps:

    $ ./manage.py migrate

## Settings

Optionally add `DJOSER` settings:

```python
DJOSER = {
    'DOMAIN': 'frontend.com',
    'SITE_NAME': 'Frontend',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
}
```

Check "Settings" section for more info.

## Endpoints

### User

Use this endpoint to retrieve/update user.

#### `GET`

URL: `/me/`

Retrieve user.

* **response**

    * status: `HTTP_200_OK` (success)

    * data:

        `{{ User.USERNAME_FIELD }}`

        `{{ User._meta.pk.name }}`

        `{{ User.REQUIRED_FIELDS }}`

#### `PUT`

URL: `/me/`

Update user.

* **request**

    * data:

        `{{ User.REQUIRED_FIELDS }}`

* **response**

    * status: `HTTP_200_OK` (success)

    * data:

        `{{ User.USERNAME_FIELD }}`

        `{{ User._meta.pk.name }}`

        `{{ User.REQUIRED_FIELDS }}`

### Register

Use this endpoint to register new user. Your user model manager should
implement [create_user](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user)
method and have [USERNAME_FIELD](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD)
and [REQUIRED_FIELDS](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS)
fields.

#### `POST`

URL: `/register/`

* **request**

    * data:

        `{{ User.USERNAME_FIELD }}`

        `{{ User.REQUIRED_FIELDS }}`

        `password`

* **response**

    * status: `HTTP_201_CREATED` (success)

    * data:

        `{{ User.USERNAME_FIELD }}`

        `{{ User._meta.pk.name }}`

        `{{ User.REQUIRED_FIELDS }}`

### Login

Use this endpoint to obtain user [authentication token](http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication).
This endpoint is available only if you are using token based authentication.

#### `POST`

URL: `/login/`

* **request**

    * data:

        `{{ User.USERNAME_FIELD }}`

        `password`

* **response**

    * status: `HTTP_200_OK` (success)

    * data:

        `auth_token`

### Logout

Use this endpoint to logout user (remove user authentication token). This endpoint is available only if you are using
token based authentication.

#### `POST`

URL: `/logout/`

* **response**

    * status: `HTTP_200_OK` (success)

### Activate

Use this endpoint to activate user account. This endpoint is not a URL which
will be directly exposed to your users - you should provide site in your
frontend application (configured by `ACTIVATION_URL`) which will send `POST`
request to activate endpoint.

#### `POST`

URL: `/activate/`

* **request**

    * data:

        `uid`

        `token`

* **response**

    * status: `HTTP_200_OK` (success)

### Set username

Use this endpoint to change user username (`USERNAME_FIELD`).

#### `POST`

URL: `/{{ User.USERNAME_FIELD }}/`

* **request**

    * data:

        `new_{{ User.USERNAME_FIELD }}`

        `re_new_{{ User.USERNAME_FIELD }}` (if `SET_USERNAME_RETYPE` is `True`)

        `current_password`

* **response**

    * status: `HTTP_200_OK` (success)

### Set password

Use this endpoint to change user password.

#### `POST`

URL: `/password/`

* **request**

    * data:

        `new_password`

        `re_new_password` (if `SET_PASSWORD_RETYPE` is `True`)

        `current_password`

* **response**

    * status: `HTTP_200_OK` (success)

### Reset password

Use this endpoint to send email to user with password reset link. You have to
setup `PASSWORD_RESET_CONFIRM_URL`.

#### `POST`

URL: `/password/reset/`

* **request**

    * data:

        `email`

* **response**

    * status: `HTTP_200_OK` (success)

### Reset password confirmation

Use this endpoint to finish reset password process. This endpoint is not a URL
which will be directly exposed to your users - you should provide site in your
frontend application (configured by `PASSWORD_RESET_CONFIRM_URL`) which
will send `POST` request to reset password confirmation endpoint.

#### `POST`

URL: `/password/reset/confirm/`

* **request**

    * data:

        `uid`

        `token`

        `new_password`

        `re_new_password` (if `PASSWORD_RESET_CONFIRM_RETYPE` is `True`)

* **response**

    * status: `HTTP_200_OK` (success)

## Settings

### DOMAIN

Domain of your frontend app. If not provided, domain of current site will be
used.

**Required**: `False`

### SITE_NAME

Name of your frontend app. If not provided, name of current site will be
used.

**Required**: `False`

### PASSWORD_RESET_CONFIRM_URL

URL to your frontend password reset page. It should contain `{uid}` and
`{token}` placeholders, e.g. `#/password-reset/{uid}/{token}`. You should pass
`uid` and `token` to reset password confirmation endpoint.

**Required**: `True`

### SEND_ACTIVATION_EMAIL

If `True`, register endpoint will send activation email to user.

**Default**: `False`

### ACTIVATION_URL

URL to your frontend activation page. It should contain `{uid}` and `{token}`
placeholders, e.g. `#/activate/{uid}/{token}`. You should pass `uid` and
`token` to activation endpoint.

**Required**: `True`

### SET_USERNAME_RETYPE

If `True`, you need to pass `re_new_{{ User.USERNAME_FIELD }}` to
`/{{ User.USERNAME_FIELD }}/` endpoint, to validate username equality.

**Default**: `False`

### SET_PASSWORD_RETYPE

If `True`, you need to pass `re_new_password` to `/password/` endpoint, to
validate password equality.

**Default**: `False`

### PASSWORD_RESET_CONFIRM_RETYPE

If `True`, you need to pass `re_new_password` to `/password/reset/confirm/`
endpoint in order to validate password equality.

**Default**: `False`

## Emails

There are few email templates which you may want to override:

* `activation_email_body.txt`
* `activation_email_subject.txt`
* `password_reset_email_body.txt`
* `password_reset_email_subject.txt`

All of them have following context:

* `user`
* `domain`
* `site_name`
* `url`
* `uid`
* `token`
* `protocol`

## Sample usage

We provide a standalone test app for you to start easily, see how everything works with basic settings. It might be useful before integrating **djoser** into your backend application.

In this extremely short tutorial we are going to mimic the simplest flow: register user, log in and log out. We will also check resource access on each consecutive step. Let's go!

* Clone repository and install **djoser** to your virtualenv:

    `$ git clone git@github.com:sunscrapers/djoser.git`

    `$ cd djoser`

    `$ pip install -e .`

* Go to the `testproject` directory, migrate the database and start the development server:

    `$ cd testproject`

    `$ ./manage.py migrate`

    `$ ./manage.py runserver 8088`

* Register a new user:

    `$ curl -X POST http://127.0.0.1:8088/auth/register/ --data 'username=djoser&password=djoser'`

    `{"email": "", "username": "djoser"}`

    So far, so good. We have just created a new user using REST API.

* Let's access user's details:

    `$ curl -X GET http://127.0.0.1:8088/auth/me/`

    `{"detail": "Authentication credentials were not provided."}`

    As we can see, we cannot access user profile without logging in. Pretty obvious.

* Let's log in:

    `curl -X POST http://127.0.0.1:8088/auth/login/ --data 'username=djoser&password=djoser'`

    `{"auth_token": "b704c9fc3655635646356ac2950269f352ea1139"}`

    We have just obtained an authorization token that we may use later in order to retrieve specific resources.

* Let's access user's details again:

    `$ curl -X GET http://127.0.0.1:8088/auth/me/`

    `{"detail": "Authentication credentials were not provided."}`

    Access is still forbidden but let's offer the token we obtained:

    `$ curl -X GET http://127.0.0.1:8088/auth/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'`

    `{"email": "", "username": "djoser"}`

    Yay, it works!

* Now let's log out:

    `curl -X POST http://127.0.0.1:8088/auth/logout/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'`

    And try access user profile again:

    `$ curl -X GET http://127.0.0.1:8088/auth/me/ -H 'Authorization: Token b704c9fc3655635646356ac2950269f352ea1139'`

    `{"detail": "Invalid token"}`

    As we can see, user has been logged out successfully and the proper token has been removed.

## Customization

If you need to override some `djoser` behaviour, you could define your custom view/serializer.

Define custom urls instead of reusing `djoser.urls`:

```python
urlpatterns = patterns('',
    (...),
    url(r'^register/$', views.CustomRegistrationView.as_view()),
)
```

Define custom view/serializer (inherit from one of `djoser` class) and override necessary method/field:

```python
class CustomRegistrationView(djoser.views.RegistrationView):

    def send_email(self, *args, **kwargs):
        your_custom_email_sender(*args, **kwargs)
```

You could check `djoser` API in source code:

* [djoser.views](https://github.com/sunscrapers/djoser/blob/master/djoser/views.py)
* [djoser.serializers](https://github.com/sunscrapers/djoser/blob/master/djoser/serializers.py)


## Development

To start developing on **djoser**, clone the repository:

`$ git clone git@github.com:sunscrapers/djoser.git`

In order to run the tests create virtualenv, go to repo directory and then:

`$ pip install -r requirements-test.txt`

`$ cd testproject`

`$ ./manage.py migrate`

`$ ./manage.py test`

## Similar projects

List of projects related to Django, REST and authentication:

- [django-rest-auth](https://github.com/Tivix/django-rest-auth)
- [django-rest-framework-digestauth](https://github.com/juanriaza/django-rest-framework-digestauth)
- [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit)
- [doac](https://github.com/Rediker-Software/doac)
- [django-rest-framework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt)
- [django-rest-framework-httpsignature](https://github.com/etoccalino/django-rest-framework-httpsignature)
- [hawkrest](https://github.com/kumar303/hawkrest)
