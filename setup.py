#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# for uploading to pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# There's some intersection with requirements.txt but pypi can't handle git
# dependencies. So it's better to just manually list dependencies again.
requires = [
    "mock",
    "sh",
]

setup(
    name="wmi-client-wrapper",
    version="0.0.12",
    description="Linux-only wrapper around wmi-client for WMI (Windows)",
    long_description=open("README.md", "r").read(),
    license="BSD",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-wmi-client-wrapper",
    packages=["wmi_client_wrapper"],
    package_dir={"wmi_client_wrapper": "wmi_client_wrapper"},
    include_package_data=True,
    install_requires=requires,
    platforms="any",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
