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


## Documentation

Documentation is available to study at
[http://djoser.readthedocs.io](http://djoser.readthedocs.io) and in
`docs` directory.

## Contributing and development

To start developing on **djoser**, clone the repository:

`$ git clone git@github.com:sunscrapers/djoser.git`

If you are a **pipenv** user you can quickly setup testing environment by
using Make commands:

`$ make init`  
`$ make test`

    You do not need to create virtualenv in this case -
    it's automatically created for you.

Otherwise, if you cannot use Make commands, please create virtualenv and install
requirements manually:  

`$ pip install django djangorestframework`  
`$ pip install -r requirements.txt`

If you are running djoser tests on Python 2.7 you also need to install `mock` library.

`$ pip install mock  # only on Python 2.7`  
`$ cd testproject`  
`$ ./manage.py test`

If you need to run tests against all supported Python and Django versions then invoke:

`$ pip install tox`  
`$ tox`

You can also play with test project by running following commands:

`$ ./manage.py migrate`  
`$ ./manage.py runserver`

## Similar projects

List of projects related to Django, REST and authentication:

- [django-rest-auth](https://github.com/Tivix/django-rest-auth)
- [django-rest-framework-digestauth](https://github.com/juanriaza/django-rest-framework-digestauth)
- [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit)
- [doac](https://github.com/Rediker-Software/doac)
- [django-rest-framework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt)
- [django-rest-framework-httpsignature](https://github.com/etoccalino/django-rest-framework-httpsignature)
- [hawkrest](https://github.com/kumar303/hawkrest)
