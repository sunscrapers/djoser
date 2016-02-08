#!/usr/bin/env python

from setuptools import find_packages, setup

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md').read()

REQUIREMENTS = [i.strip() for i in open('requirements.txt').readlines()]

setup(
    name='djoser',
    version='0.2.1',
    packages=find_packages(include=('djoser*',)),
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=description,
    install_requires=REQUIREMENTS,
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
