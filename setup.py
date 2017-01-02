#!/usr/bin/env python

import io
import os
from setuptools import setup


try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = io.open('README.md', encoding='utf-8').read()


def get_packages(package):
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_requirements(file_name):
    return [i.strip() for i in open(file_name).readlines()]


setup(
    name='djoser',
    version='0.5.2',
    packages=get_packages('djoser'),
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=description,
    install_requires=get_requirements('requirements.txt'),
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
