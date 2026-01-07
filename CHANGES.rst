dsmtpd Changelog
================

Here you can see the full list of changes between each dsmtpd release.

Version 1.2.0
-------------

Released on January 7th 2026.

Features:

- Document SMTPUTF8 support (RFC 6531) - enabled by default via aiosmtpd (#32)
- SMTPUTF8 allows UTF-8 email addresses, headers, and message content
- Add ``--disable-smtputf8`` CLI option to disable SMTPUTF8 extension for legacy client compatibility (#34)

Development improvements:

- Add test coverage reporting with pytest-cov (#29)
- Add code quality tools: ruff (linting/formatting) and mypy (type checking) (#29)
- Add pre-commit hooks with prek for automated code quality checks (#31)
- New make targets: ``lint``, ``lint-fix``, ``format``, ``typecheck`` (#29)
- Enhanced Makefile with automatic virtual environment management
- Add smart dependency tracking to avoid unnecessary reinstallations during development
- New make targets: ``install-dev``, ``clean``, ``clean-build``, ``clean-venv``
- Makefile now uses Python from asdf/mise for consistent development environments
- Significantly faster repeated test runs with timestamp-based dependency tracking
- Add comprehensive tests for the debugging SMTP server (#8)
- New integration tests for email reception, storage, and multipart email handling
- Add tests for ``--version`` flag and ``--max-size`` option (#29)
- Add test for SMTPUTF8 support verification (#32)
- Add support for Python 3.14 (#25)
- Replace deprecated license classifiers with SPDX license expression (#24)
- GitHub Actions workflow now includes linting and type checking jobs (#29)

Version 1.1
-----------

Released on September 13th 2025.

- Lower Python version requirement from 3.12 to 3.10 (#17)
- Fix crash when directory exists but is not yet a valid Maildir with proper validation and repair functionality (#18)
- Add exit codes documentation to README
- Code formatting improvements with ruff

Version 1.0
-----------

Release on May 20th 2025.

- Migration to aiosmtpd to Support Python >= 3.12 (#11, patch by Sebastian Wagner)
- Add minimal tests for maildir check and importability
- Add systemd service file (by Sebastian Wagner)

Version 0.3
-----------

Release on May 26th 2021.

- Maildir capture: added early check (patch by Bernhard E. Reiter)
- Remove the support of Docopt
- Remove the support of Python 2.x (dead in 2020)
- Support Python 3.6+
- Improve the classifiers for PyPI
- Migrate to PEP 517
- Fix License into setup.py
- Add tests for the CLI using argparse instead of docopt

Version 0.2
-----------

Release on January 21st 2013.

- Allow to store the incoming emails in a maildir via the '-d' argument

Version 0.1
-----------

Release on January 14th 2013.

- Implement a basic server
- Show the message in the log
