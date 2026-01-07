dsmptd: A debugger SMTP server for Humans
=========================================

.. image:: https://github.com/matrixise/dsmtpd/workflows/Tests/badge.svg
   :target: https://github.com/matrixise/dsmtpd/actions/workflows/tests.yml
   :alt: Tests Status

dsmtpd is a small tool to help the developer without an smtp server

**Python Support:** Python 3.10, 3.11, 3.12, 3.13, 3.14

Usage
-----

::

    $ dsmtpd -p 1025 -i 127.0.0.1
    2013-01-13 14:00:07,346 INFO: Starting SMTP server at 127.0.0.1:1025


Installation
------------

For the installation, we recommend to use a virtualenv, it's the easy way if you want to discover this package::

    virtualenv ~/.envs/dsmtpd
    source ~/.envs/dsmtpd/bin/activate

    pip install dsmtpd

Documentation
-------------

Execute dsmtpd with the --help flag and you will get the usage of this command::

    dsmtpd --help

There are three options:

* -p You specify the port of dsmtpd (default is 1025)
* -i You specify the network interface (default is loopback, 127.0.0.1)
* -d You specify a Maildir directory to save the incoming emails

Use it
------

Here is a small example::

    dsmtpd

    swaks --from stephane@wirtel.be --to foo@bar.com  --server localhost --port 1025

Exit Codes
----------

``dsmtpd`` uses specific exit codes to indicate the result of its execution.

+------+---------------------------+--------------------------------------------+
| Code | Meaning                   | Example                                    |
+======+===========================+============================================+
| 0    | Success                   | Normal shutdown (e.g. user pressed         |
|      |                           | ``Ctrl+C``) or clean termination.          |
+------+---------------------------+--------------------------------------------+
| 2    | Invalid Maildir directory | The given path exists but does not contain |
|      |                           | the required subfolders: ``tmp``, ``new``, |
|      |                           | and ``cur``.                               |
+------+---------------------------+--------------------------------------------+

Contributing
------------

Clone the repository::

    git clone git://github.com/matrixise/dsmtpd.git
    cd dsmtpd

Development
-----------

The project includes a Makefile to simplify development tasks. It automatically manages
a virtual environment and dependencies using Python from asdf or mise.

**Quick Start**

Set up your development environment::

    make install-dev

This creates a ``.venv`` virtual environment and installs all development dependencies.

**Available Make Targets**

* ``make install-dev`` - Set up development environment (creates venv and installs dependencies)
* ``make test`` - Run tests with pytest (automatically installs dependencies if needed)
* ``make build`` - Build distribution packages
* ``make clean`` - Remove all build artifacts and virtual environment
* ``make clean-build`` - Remove only build artifacts (dist/, build/, *.egg-info)
* ``make clean-venv`` - Remove only the virtual environment

**Workflow Tips**

The Makefile uses smart dependency tracking. Running ``make test`` multiple times will only
reinstall dependencies if ``requirements-dev.txt`` or ``setup.cfg`` have changed, making
repeated test runs much faster.

To force a fresh installation of dependencies::

    make install-dev

**Running Tests**

After setting up the development environment::

    make test

Or directly with pytest::

    .venv/bin/pytest


Copyright 2013 (c) by Stephane Wirtel
