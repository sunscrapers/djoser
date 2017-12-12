#!/usr/bin/env python

import os
from setuptools import setup


with open('README.rst', 'r') as f:
    readme = f.read()


def get_packages(package):
    return [
        dirpath for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


setup(
    name='djoser',
    version='1.1.5',
    packages=get_packages('djoser'),
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=readme,
    install_requires=['django-templated-mail'],
    include_package_data=True,
    url='https://github.com/sunscrapers/djoser',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
