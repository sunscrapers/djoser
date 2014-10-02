# djoser

[![Build Status](https://travis-ci.org/sunscrapers/djoser.svg?branch=master)](https://travis-ci.org/sunscrapers/djoser)

REST version of Django authentication system. **djoser** is set of
[Django Rest Framework](http://www.django-rest-framework.org/) views to handle
such things as registration, login and password reset. It works with custom
user model.

Instead of reusing Django code (e.g. `PasswordResetForm`), we reimplemented
few things to fit better into Single Page App architecture.

Developed by [SUNSCRAPERS](http://sunscrapers.com/) with passion & patience.

Available endpoints:

 * `/register`
 * `/login`
 * `/activate`
 * `/username`
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

    $ pip install git+https://github.com/sunscrapers/djoser.git
    
## Usage

Configure `INSTALLED_APPS`:
        
    INSTALLED_APPS = (
        'django.contrib.auth',
        (...), 
        'rest_framework',
        'rest_framework.authtoken',
        'djoser',
        (...), 
    )
    
Add `djoser` settings:

    DJOSER = {
        'DOMAIN': 'frontend.com',
        'SITE_NAME': 'Frontend',
        'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
        'ACTIVATION_URL': '#/activate/{uid}/{token}',
        'LOGIN_AFTER_REGISTRATION': True,
        'LOGIN_AFTER_ACTIVATION': True,
        'SEND_ACTIVATION_EMAIL': True,
    }
    
Configure `urls.py`:

    urlpatterns = patterns('',
        (...),
        url(r'^auth/', include('djoser.urls')),
    )
    
## Endpoints
    
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

If `LOGIN_AFTER_ACTIVATION` setting is `True`, you will receive authentication 
token withing response.

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

URL: `/username`

Methods: `POST`

`POST` request data:

* `new_username1`
* `new_username2`
* `current_password`

Use this endpoint to change user username (`USERNAME_FIELD`).

### Set password

URL: `/password`

Methods: `POST`

`POST` request data:

* `new_password1`
* `new_password2`
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

## TODO

Upcoming features:

* **documentation**
* "retype" enable/disable
* registration customization (custom fields/profile, post-registration action)
* password reset customization (custom HTML templates)
* endpoints documentation
* logout/token expired view (?)
* user retrieve view
