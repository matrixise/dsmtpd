#!/usr/bin/env python
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2013 by Stephane Wirtel <stephane@wirtel.be>
    :license: BSD, see LICENSE for more details
"""
import os
from setuptools import setup
from setuptools import find_packages

from dsmtpd import __version__
from dsmtpd import __name__
from dsmtpd import __author__
from dsmtpd import __author_email__


HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, 'requirements.txt')) as fp:
    requirements = fp.readlines()

with open('README.rst') as f:
    README = f.read()

with open('CHANGES.rst') as f:
    CHANGES = f.read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3 :: Only"
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Communications :: Email",
]

setup(
    name=__name__,
    version=__version__,
    url='https://github.com/matrixise/dsmtpd',
    description=('Simple SMTP Server for debugging'),
    long_description='\n'.join([README, CHANGES]),
    author=__author__,
    author_email=__author_email__,
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    classifiers=classifiers,
    entry_points="""
    [console_scripts]
    dsmtpd = dsmtpd.__main__:main
    """
)
