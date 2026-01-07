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

Command-Line Options
--------------------

``-p PORT, --port PORT``
    Specify the port to listen on. Default: **1025**

``-i INTERFACE, --interface INTERFACE``
    Specify the network interface to bind to. Default: **127.0.0.1** (loopback)

``-d DIRECTORY, --directory DIRECTORY``
    Specify a Maildir directory to save incoming emails. Default: current directory

``-s SIZE, --max-size SIZE``
    Maximum message size in bytes. Use **0** for no limit. Default: **33554432** (32 MiB)

``--disable-smtputf8``
    Disable SMTPUTF8 extension for legacy SMTP client compatibility. Default: **enabled**

``--version``
    Show program version and exit

``-h, --help``
    Show help message and exit

Usage Examples
--------------

Start server with default settings (port 1025, localhost)::

    dsmtpd

Start server on custom port::

    dsmtpd -p 2525

Bind to all interfaces::

    dsmtpd -i 0.0.0.0 -p 25

Save emails to specific Maildir::

    dsmtpd -d /path/to/maildir

Limit message size to 10 MB::

    dsmtpd --max-size 10485760

Disable UTF-8 support for legacy clients::

    dsmtpd --disable-smtputf8

Send a test email with swaks::

    swaks --from sender@example.com --to recipient@example.com --server localhost --port 1025

Features
--------

**SMTPUTF8 Support**

dsmtpd has built-in support for SMTPUTF8 (RFC 6531), which allows email addresses and content to contain UTF-8 characters. This feature is **enabled by default** and requires no configuration.

SMTPUTF8 enables:

* Email addresses with international characters (e.g., ``用户@例え.jp``)
* UTF-8 encoded message headers and body content
* Full Unicode support in SMTP transactions

Example usage with UTF-8 email addresses::

    swaks --from user@example.com --to 用户@例え.jp --server localhost --port 1025

This functionality is provided by the underlying aiosmtpd library and works transparently with all standard SMTP clients that support the SMTPUTF8 extension.

**Disabling SMTPUTF8**

If you need to test compatibility with legacy SMTP clients or reproduce encoding issues, you can disable SMTPUTF8::

    dsmtpd --disable-smtputf8

When disabled, the server will not advertise SMTPUTF8 support and will only accept ASCII email addresses and content.

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

Development Workflow:

* ``make install-dev`` - Set up development environment (creates venv and installs dependencies)
* ``make test`` - Run tests with pytest (automatically installs dependencies if needed)
* ``make lint`` - Check code quality with ruff linter
* ``make lint-fix`` - Auto-fix linting issues and format code with ruff
* ``make format`` - Format code with ruff format
* ``make typecheck`` - Run mypy type checking

Build and Release:

* ``make build`` - Build distribution packages
* ``make check-dist`` - Verify distribution package integrity

Cleanup:

* ``make clean`` - Remove all build artifacts and virtual environment
* ``make clean-build`` - Remove only build artifacts (dist/, build/)
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

**Code Quality & Pre-commit Hooks**

The project uses `prek <https://github.com/j178/prek>`_ to simplify pre-commit hook setup.

After installing development dependencies, set up pre-commit hooks::

    prek install

This automatically installs git hooks that will:

* Run ``ruff`` linter with auto-fix
* Run ``ruff format`` for code formatting
* Run ``mypy`` for type checking

You can also run quality checks manually::

    make lint        # Check code quality
    make lint-fix    # Auto-fix linting issues
    make format      # Format code
    make typecheck   # Run mypy type checking

The pre-commit hooks ensure code quality before commits, catching issues early and
maintaining consistent code standards across all contributions.


Copyright 2013 (c) by Stephane Wirtel
