#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from setuptools import setup

__version__ = '1.0'  # identify main version of dohq-tfs tool
devStatus = '4 - Beta'  # default build status, see: https://pypi.python.org/pypi?%3Aaction=list_classifiers

if 'TRAVIS_BUILD_NUMBER' in os.environ and 'TRAVIS_BRANCH' in os.environ:
    print("This is TRAVIS-CI build")
    print("TRAVIS_BUILD_NUMBER = {}".format(os.environ['TRAVIS_BUILD_NUMBER']))
    print("TRAVIS_BRANCH = {}".format(os.environ['TRAVIS_BRANCH']))

    __version__ += '.{}{}'.format(
        '' if 'release' in os.environ['TRAVIS_BRANCH'] or os.environ['TRAVIS_BRANCH'] == 'master' else 'dev',
        os.environ['TRAVIS_BUILD_NUMBER'],
    )

    devStatus = '5 - Production/Stable' if 'release' in os.environ['TRAVIS_BRANCH'] or os.environ[
                                                                                           'TRAVIS_BRANCH'] == 'master' else devStatus

else:
    print("This is local build")
    __version__ += '.dev0'  # set version as major.minor.localbuild if local build: python setup.py install

print("dohq-tfs build version = {}".format(__version__))

setup(
    name='dohq-tfs',

    version=__version__,

    description='Microsoft TFS Python Library (TFS API Python client) that can work with TFS workflow and workitems.',

    long_description='You can see detailed user manual here: https://devopshq.github.io/tfs/',

    license='MIT',

    author='Alexey Burov',

    author_email='allburov@gmail.com',

    url='https://devopshq.github.io/tfs/',

    download_url='https://github.com/devopshq/tfs.git',

    entry_points={},

    classifiers=[
        'Development Status :: {}'.format(devStatus),
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],

    packages=[
        'tfs',
    ],

    setup_requires=[
        'pytest-runner'
    ],

    tests_require=[
        'pytest==3.1.2',
        'HTTPretty',
        'pytest_httpretty',
    ],

    install_requires=[
        'requests',
        'requests_ntlm'
    ],

    package_data={
        '': [
            '../LICENSE',
            '../README.md',
        ],
    },

    zip_safe=True,
)
