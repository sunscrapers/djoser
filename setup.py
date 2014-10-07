#!/usr/bin/env python

from setuptools import setup

setup(
    name='djoser',
    version='0.0.1',
    packages=['djoser'],
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=open('README.md').read(),
    install_requires=[
      'Django>=1.5',
      'djangorestframework>=2.4.0',
    ],
    tests_require=[
       'djet>=0.0.10'
    ],
    include_package_data=True,
    zip_safe=False,
)
