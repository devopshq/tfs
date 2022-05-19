#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="dohq-tfs",
    version="1.1.1",
    description="Microsoft TFS Python Library (TFS API Python client) that can work with TFS workflow and workitems.",
    long_description="You can see detailed user manual here: https://devopshq.github.io/tfs/",
    license="MIT",
    author="Alexey Burov",
    author_email="allburov@gmail.com",
    url="https://devopshq.github.io/tfs/",
    download_url="https://github.com/devopshq/tfs.git",
    entry_points={},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.4",
    ],
    packages=[
        "tfs",
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest==3.1.2",
        "HTTPretty",
        "pytest_httpretty",
    ],
    install_requires=[
        "requests",
        "requests_ntlm",
        "six",
    ],
    package_data={
        "": [
            "../LICENSE",
            "../README.md",
        ],
    },
    zip_safe=True,
)
