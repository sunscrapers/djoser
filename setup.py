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
    version='0.7.0',
    packages=get_packages('djoser'),
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=readme,
    install_requires=[],
    include_package_data=True,
    url='https://github.com/sunscrapers/djoser',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
