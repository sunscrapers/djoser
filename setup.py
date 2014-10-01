#!/usr/bin/env python

from setuptools import setup

setup(
    name='djoser',
    packages=['djoser'],
    install_requires=[
       'Django>=1.7',
       'djangorestframework>=2.4.3',
    ],
    tests_require=[
        'djet>=0.0.9'
    ],
    package_data={
        'templates': ['templates/*.html', 'templates/*.txt']
    },
)
