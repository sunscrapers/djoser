# djoser

[![Build Status](https://travis-ci.org/sunscrapers/djoser.svg?branch=master)](https://travis-ci.org/sunscrapers/djoser)

REST version of [Django](https://www.djangoproject.com/) authentication system. 
**djoser** is set of [Django Rest Framework](http://www.django-rest-framework.org/)
views to handle such things as registration, login and password reset. It
works with [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/).

Instead of reusing Django code (e.g. `PasswordResetForm`), we reimplemented
few things to fit better into [Single Page App](http://en.wikipedia.org/wiki/Single-page_application)
architecture.

Developed by [SUNSCRAPERS](http://sunscrapers.com/) with passion & patience.

Available endpoints:

 * `/me`
 * `/register`
 * `/login`
 * `/activate`
 * `/{{ User.USERNAME_FIELD }}`
 * `/password`
 * `/password/reset`
 * `/password/reset/confirm`
 
Supported Python versions:

 * Python 2.7
 * Python 3.4
 
Supported Django versions:

 * Django 1.5
 * Django 1.6
 * Django 1.7

## Installation

Use `pip`:

    $ pip install djoser
    
## Usage

Configure `INSTALLED_APPS`:

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
    
Configure `urls.py`:

```python
urlpatterns = patterns('',
    (...),
    url(r'^auth/', include('djoser.urls')),
)
```

Optionally add `djoser` settings:

```python
DJOSER = {
    'DOMAIN': 'frontend.com',
    'SITE_NAME': 'Frontend',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'LOGIN_AFTER_ACTIVATION': True,
    'SEND_ACTIVATION_EMAIL': True,
}
```

Check [settings](#settings) section for more info.
    
## Endpoints
    
### User

URL: `/me`

Methods: `GET`, `PUT`

`PUT` request data:

* `{{ User.REQUIRED_FIELDS }}`

`PUT` and `GET` response data:

* `{{ User.USERNAME_FIELD }}`
* `{{ User.REQUIRED_FIELDS }}`

Use this endpoint to retrieve/update user.

### Register

URL: `/register`

Methods: `POST`

`POST` request data:

* `{{ User.USERNAME_FIELD }}`
* `{{ User.REQUIRED_FIELDS }}`
* `password`

`POST` response data:

* `{{ User.USERNAME_FIELD }}`
* `{{ User.REQUIRED_FIELDS }}`
* `auth_token` (if `LOGIN_AFTER_ACTIVATION` is `True`)

Use this endpoint to register new user. Your user model manager should
implement [`create_user`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user)
method and have [`USERNAME_FIELD`](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD)
and [`REQUIRED_FIELDS`](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS)
fields.

If `LOGIN_AFTER_ACTIVATION` is `True`, you will receive authentication token
within response.

### Login

URL: `/login`

Methods: `POST`

`POST` request data:

* `{{ User.USERNAME_FIELD }}`
* `password`

`POST` response data:

* `auth_token`

Use this endpoint to obtain user [authentication token](http://www.django-rest-framework.org/api-guide/authentication#tokenauthentication).

### Activate

URL: `/activate`

Methods: `POST`

`POST` request data:

* `uid`
* `token`

`POST` response data:

* `auth_token` (if `LOGIN_AFTER_ACTIVATION` is `True`)

Use this endpoint to activate user account.

### Set username

URL: `/{{ User.USERNAME_FIELD }}`

Methods: `POST`

`POST` request data:

* `new_{{ User.USERNAME_FIELD }}`
* `re_new_{{ User.USERNAME_FIELD }}` (if `SET_USERNAME_RETYPE` is `True`)
* `current_password`

Use this endpoint to change user username (`USERNAME_FIELD`).

### Set password

URL: `/password`

Methods: `POST`

`POST` request data:

* `new_password`
* `re_new_password` (if `SET_PASSWORD_RETYPE` is `True`)
* `current_password`

Use this endpoint to change user password.

### Reset password

URL: `/password/reset`

Methods: `POST`

`POST` request data:

* `email`

Use this endpoint to send email to user with password reset link. You have to 
setup `DOMAIN`, `SITE_NAME`, `PASSWORD_RESET_CONFIRM_URL`.

### Reset password confirmation

URL: `/password/reset/confirm`

Methods: `POST`

`POST` request data:

* `uid`
* `token`
* `new_password`
* `re_new_password` (if `PASSWORD_RESET_CONFIRM_RETYPE` is `True`)

Use this endpoint to finish reset password process.
 
## Settings

#### `LOGIN_AFTER_REGISTRATION`

If `True`, register endpoint will return `auth_token` within response.

Default: `False`

#### `DOMAIN`

Domain of your frontend app. Default: `''`.

#### `SITE_NAME`

Name of your frontend app. Default: `''`.

#### `PASSWORD_RESET_CONFIRM_URL`

URL to your frontend password reset page. It should containt `{uid}` and
`{token}` placeholders, e.g. `#/password-reset/{uid}/{token}`. Default: `''`.

#### `SEND_ACTIVATION_EMAIL`

If `True`, register endpoint will send activation email to user.
 
#### `ACTIVATION_URL`

URL to your frontend activation page. It should containt `{uid}` and `{token}`
placeholders, e.g. `#/activate/{uid}/{token}`. Default: `''`.

#### `LOGIN_AFTER_ACTIVATION`

If `True`, activate endpoint will return `auth_token` within response.

Default: `False`

#### `SET_USERNAME_RETYPE`

If `True`, you need to pass `re_new_{{ User.USERNAME_FIELD }}` to
`/{{ User.USERNAME_FIELD }}` endpoint, to validate username equality.

Default: `False`

#### `SET_PASSWORD_RETYPE`

If `True`, you need to pass `re_new_password` to `/password` endpoint, to
validate password equality.

Default: `False`

#### `PASSWORD_RESET_CONFIRM_RETYPE`

If `True`, you need to pass `re_new_password` to `/password/reset/confirm`
endpoint, to validate password equality.

Default: `False`

## Emails

There are few email templates which you could override:
 
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

## Customization

If you need to override some `djoser` behaviour, you could define your custom view/serializer.

Define custom urls instead of reusing `djoser.urls`:

```python
urlpatterns = patterns('',
    (...),
    url(r'^register$', views.CustomRegistrationView.as_view()),
)
```

Define custom view/serializer (inherit from one of `djoser` class) and override necessary method/field:

```python
class CustomRegistrationView(djoser.views.RegistrationView):

    def send_email(self, *args, **kwargs):
        your_custom_email_sender(*args, **kwargs)
```

You could check `djoser` API in source code:

* [`djoser.views`](https://github.com/sunscrapers/djoser/blob/master/djoser/views.py)
* [`djoser.serializers`](https://github.com/sunscrapers/djoser/blob/master/djoser/serializers.py)

## Similar projects

List of projects related to Django, REST and authentication:

- [django-rest-auth](https://github.com/Tivix/django-rest-auth)
- [django-rest-framework-digestauth](https://github.com/juanriaza/django-rest-framework-digestauth)
- [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit)
- [doac](https://github.com/Rediker-Software/doac)
- [django-rest-framework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt)
- [django-rest-framework-httpsignature](https://github.com/etoccalino/django-rest-framework-httpsignature)
- [hawkrest](https://github.com/kumar303/hawkrest)
