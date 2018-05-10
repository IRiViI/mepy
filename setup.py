#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'netifaces',
    'asyncio',
    'websocket',
    'tornado',
    'websocket-client'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Hendrik Willem Vink",
    author_email='rckvnk@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Machine Engine connect and develop faster",
    entry_points={
        'console_scripts': [
            'mepy=mepy.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='mepy',
    name='mepy',
    packages=find_packages(include=['mepy'],exclude=['*tests','examples*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/IRiViI/mepy',
    version='0.2.1',
    zip_safe=False,
)
