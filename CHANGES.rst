dsmtpd Changelog
================

Here you can see the full list of changes between each dsmtpd release.

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
