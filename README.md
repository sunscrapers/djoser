# djoser

[![Build Status](https://travis-ci.org/sunscrapers/djoser.svg?branch=master)](https://travis-ci.org/sunscrapers/djoser)

REST version of Django authentication system. **djoser** is set of
[Django Rest Framework](http://www.django-rest-framework.org/) views to handle
such things as registration, login and password reset. It works with custom
user model.

Instead of reusing Django code (e.g. `PasswordResetForm`), we were 
reimplemented few things to fit better into Single Page App architecture.

Developed by [SUNSCRAPERS](http://sunscrapers.com/) with passion & patience.

Available endpoints:

 * `/register`
 * `/login`
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
        (...), 
    )
    
Add `djoser` settings:

    DJOSER = {
        'DOMAIN': 'frontend.com',
        'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm',
    }
    
Configure `urls.py`:

    urlpatterns = patterns('',
        (...),
        url(r'^auth/', include('djoser.urls')),
    )
    
## TODO

Upcoming features:

* registration customization (custom fields/profile, post-registration action)
* password reset customization (custom HTML templates)
* user auto login after registration (return token)
* endpoints documentation
* logout/token expired view (?)
* user retrieve view
* user email verify view
