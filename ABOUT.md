# dsmtpd: A Debugging SMTP Server for Developers

## What is dsmtpd?

**dsmtpd** (Debugging SMTP Daemon) is a lightweight, developer-friendly SMTP server designed for local development and testing. It provides a simple way to test email functionality in applications without needing a full production SMTP server or risking sending test emails to real recipients.

Think of it as a **"fake SMTP server"** that catches all your test emails, allowing you to inspect them locally during development.

## Why dsmtpd?

### The Problem
When developing applications that send emails, developers face common challenges:
- Setting up a real SMTP server is complex and overkill for testing
- Sending test emails to real addresses is risky and unprofessional
- Cloud email services require configuration and may have sending limits
- Debugging email content and headers is difficult without proper tools

### The Solution
dsmtpd solves these problems by providing:
- **Zero-configuration setup** - Works out of the box with sensible defaults
- **Local-only operation** - Emails never leave your machine
- **Maildir storage** - Optionally save emails for inspection
- **Console logging** - See email metadata instantly in your terminal
- **Modern standards** - Full SMTPUTF8 support for international email addresses

## Key Features

### 1. Simple to Use
```bash
# Start server (default: localhost:1025)
$ dsmtpd

# Custom configuration
$ dsmtpd -p 2525 -d /tmp/maildir
```

### 2. SMTPUTF8 Support (RFC 6531)
- Handles international email addresses (e.g., `用户@例え.jp`)
- UTF-8 content in headers and message body
- Enabled by default, can be disabled for legacy testing

### 3. Flexible Storage Options
- **Console mode**: Log email metadata to terminal
- **Maildir mode**: Save emails to standard Maildir format for later inspection
- **Size limits**: Configurable maximum message size (default 32 MiB)

### 4. Developer-Friendly
- Real-time logging of sender, recipients, and subject
- Python 3.10+ support (including latest Python 3.14)
- Single command installation: `pip install dsmtpd`
- No external dependencies beyond Python and aiosmtpd

### 5. Production-Ready Architecture
- Built on aiosmtpd (asyncio-based)
- Handles multiple concurrent connections
- Proper exit codes for automation
- Systemd service file included

## Common Use Cases

### Local Development
```bash
# Start dsmtpd on default port
$ dsmtpd

# Configure your app to use localhost:1025 as SMTP server
# All emails are captured and logged
```

### Integration Testing
```bash
# Save emails to Maildir for automated testing
$ dsmtpd -d /tmp/test-maildir

# Your tests can inspect the Maildir to verify email sending
```

### Email Template Development
```bash
# Capture emails to inspect HTML/text content
$ dsmtpd -d ~/email-templates

# Send test emails and review them in your mail client
```

### Legacy System Testing
```bash
# Test with SMTPUTF8 disabled
$ dsmtpd --disable-smtputf8

# Verify compatibility with older SMTP clients
```

## Quick Start

### Installation
```bash
pip install dsmtpd
```

### Basic Usage
```bash
# Start server
$ dsmtpd
2024-01-07 14:00:07 INFO: Starting dsmtpd 1.2.0 at 127.0.0.1:1025

# In another terminal, send a test email
$ swaks --from developer@example.com \
        --to test@example.com \
        --server localhost \
        --port 1025

# See the email logged in dsmtpd console
INFO: 127.0.0.1:12345: developer@example.com -> test@example.com [Test Email]
```

### With Maildir Storage
```bash
# Create and use Maildir
$ dsmtpd -d ~/test-emails

# Emails are stored in ~/test-emails/new/
# Read them with any mail client or directly
```

## Technical Details

### Architecture
- **Language**: Python 3.10+
- **SMTP Engine**: aiosmtpd (asyncio-based)
- **Storage**: Maildir format (optional)
- **Concurrency**: Handles multiple connections asynchronously

### Configuration Options
| Option | Description | Default |
|--------|-------------|---------|
| `-p, --port` | Server port | 1025 |
| `-i, --interface` | Network interface | 127.0.0.1 |
| `-d, --directory` | Maildir storage path | None (console only) |
| `-s, --max-size` | Max message size | 32 MiB |
| `--disable-smtputf8` | Disable UTF-8 support | Enabled |

### Exit Codes
- **0**: Success (normal shutdown)
- **2**: Invalid Maildir directory structure

### Development Tools
The project includes comprehensive development tooling:
- **Testing**: pytest with 64% code coverage
- **Linting**: ruff for code quality
- **Type checking**: mypy for static analysis
- **Pre-commit hooks**: prek for automated quality checks

## Who Uses dsmtpd?

### Target Audience
- Web application developers testing email features
- DevOps engineers setting up CI/CD pipelines
- QA engineers verifying email functionality
- Email template designers previewing messages
- System administrators testing mail configurations

### Perfect For
- ✅ Django/Flask/FastAPI applications
- ✅ Node.js/Ruby/PHP backend services
- ✅ Automated testing suites
- ✅ Docker development environments
- ✅ Local WordPress/Drupal development

### Not Suitable For
- ❌ Production email sending
- ❌ Email relay/forwarding
- ❌ Internet-facing SMTP server
- ❌ Spam filtering or virus scanning

## Project Information

- **Author**: Stéphane Wirtel
- **License**: BSD
- **Source**: https://github.com/matrixise/dsmtpd
- **PyPI**: https://pypi.org/project/dsmtpd/
- **Python**: 3.10, 3.11, 3.12, 3.13, 3.14
- **First Release**: January 2013
- **Latest Version**: 1.2.0 (January 2026)

## Evolution

dsmtpd has evolved significantly since its inception:

**v0.1 (2013)**: Basic SMTP server with console logging
**v1.0 (2025)**: Migration to aiosmtpd for Python 3.12+ support
**v1.1 (2025)**: Enhanced Maildir validation and error handling
**v1.2 (2026)**:
- SMTPUTF8 support documented
- Code quality tools (ruff, mypy)
- Pre-commit hooks with prek
- Comprehensive test suite
- CLI option to disable UTF-8 for legacy testing

## Getting Help

- **Documentation**: Full README at https://github.com/matrixise/dsmtpd
- **Issues**: Report bugs at https://github.com/matrixise/dsmtpd/issues
- **Community**: Open source, contributions welcome

---

*dsmtpd: Making email development simple since 2013*
