#!/usr/bin/env python

from setuptools import setup

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    description = open('README.md').read()


setup(
    name='djoser',
    version='0.0.3',
    packages=['djoser'],
    license='MIT',
    author='SUNSCRAPERS',
    description='REST version of Django authentication system.',
    author_email='info@sunscrapers.com',
    long_description=description,
    install_requires=[
      'Django>=1.5',
      'djangorestframework>=2.4.0',
    ],
    tests_require=[
       'djet>=0.0.10'
    ],
    include_package_data=True,
    zip_safe=False,
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
