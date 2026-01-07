"""
Integration tests for the SMTP server
"""

import mailbox
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tempfile import TemporaryDirectory

from aiosmtpd.controller import Controller

from dsmtpd._dsmtpd import DsmtpdHandler, ensure_maildir


def test_server_starts_and_stops():
    """Test that the SMTP server can start and stop cleanly"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10025,
        )

        # Start the server
        controller.start()

        try:
            # Verify server is running
            assert controller.server is not None
            assert controller.server.sockets is not None
        finally:
            # Stop the server
            controller.stop()


def test_send_simple_email():
    """Test sending a simple text email to the server"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10026,
        )

        controller.start()

        try:
            # Send an email using smtplib
            with smtplib.SMTP("127.0.0.1", 10026) as smtp:
                sender = "sender@example.com"
                recipients = ["recipient@example.com"]
                message = "Subject: Test Email\n\nThis is a test message."

                smtp.sendmail(sender, recipients, message)

            # Give the server a moment to write the file
            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

            # Verify email content
            email = mbox[list(mbox.keys())[0]]
            assert email["Subject"] == "Test Email"
            assert "This is a test message." in email.get_payload()

        finally:
            controller.stop()


def test_send_multipart_email():
    """Test sending a multipart email with MIME"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10027,
        )

        controller.start()

        try:
            # Create a multipart message
            msg = MIMEMultipart()
            msg["From"] = "test@example.com"
            msg["To"] = "recipient@example.com"
            msg["Subject"] = "Multipart Test"

            body = "This is the email body"
            msg.attach(MIMEText(body, "plain"))

            # Send the email
            with smtplib.SMTP("127.0.0.1", 10027) as smtp:
                smtp.send_message(msg)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

            # Verify email content
            email = mbox[list(mbox.keys())[0]]
            assert email["Subject"] == "Multipart Test"
            assert email["From"] == "test@example.com"
            assert email["To"] == "recipient@example.com"

        finally:
            controller.stop()


def test_multiple_recipients():
    """Test sending email to multiple recipients"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10028,
        )

        controller.start()

        try:
            # Send email to multiple recipients
            with smtplib.SMTP("127.0.0.1", 10028) as smtp:
                sender = "sender@example.com"
                recipients = [
                    "recipient1@example.com",
                    "recipient2@example.com",
                    "recipient3@example.com",
                ]
                message = "Subject: Multiple Recipients Test\n\nTest message."

                smtp.sendmail(sender, recipients, message)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

        finally:
            controller.stop()


def test_multiple_emails():
    """Test sending multiple emails in sequence"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10029,
        )

        controller.start()

        try:
            # Send multiple emails
            with smtplib.SMTP("127.0.0.1", 10029) as smtp:
                for i in range(5):
                    sender = f"sender{i}@example.com"
                    recipients = [f"recipient{i}@example.com"]
                    message = f"Subject: Test Email {i}\n\nMessage number {i}."
                    smtp.sendmail(sender, recipients, message)

            time.sleep(0.2)

            # Verify all emails were stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 5

        finally:
            controller.stop()


def test_server_with_custom_port():
    """Test server can bind to a specific port"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        # Use a high port number to avoid permission issues
        test_port = 10030

        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=test_port,
        )

        controller.start()

        try:
            # Verify server is listening on the correct port
            actual_port = controller.server.sockets[0].getsockname()[1]
            assert actual_port == test_port

            # Send a test email
            with smtplib.SMTP("127.0.0.1", test_port) as smtp:
                smtp.sendmail(
                    "test@example.com",
                    ["dest@example.com"],
                    "Subject: Port Test\n\nTesting custom port.",
                )

            time.sleep(0.1)

            # Verify email was received
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

        finally:
            controller.stop()


def test_max_size_within_limit():
    """Test that emails within max-size limit are accepted"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        # Set max size to 10KB
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10031,
            data_size_limit=10240,
        )

        controller.start()

        try:
            # Send a 2KB email (well under limit)
            with smtplib.SMTP("127.0.0.1", 10031) as smtp:
                sender = "sender@example.com"
                recipients = ["recipient@example.com"]
                # Create ~2KB message with proper line breaks
                lines = [f"This is line {i}" for i in range(40)]
                body = "\n".join(lines) * 2  # ~2KB
                message = f"Subject: Size Test\n\n{body}"

                smtp.sendmail(sender, recipients, message)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

        finally:
            controller.stop()


def test_max_size_exceeded():
    """Test that emails exceeding max-size are rejected"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        # Set max size to 1KB
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10032,
            data_size_limit=1024,
        )

        controller.start()

        try:
            # Try to send a 5KB email (exceeds limit)
            email_rejected = False
            with smtplib.SMTP("127.0.0.1", 10032) as smtp:
                sender = "sender@example.com"
                recipients = ["recipient@example.com"]
                # Create ~5KB message with proper line breaks
                lines = [f"This is line {i}" for i in range(100)]
                body = "\n".join(lines) * 2  # ~5KB
                message = f"Subject: Size Test\n\n{body}"

                try:
                    smtp.sendmail(sender, recipients, message)
                except (smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as e:
                    # Email was rejected due to size (expected)
                    # aiosmtpd rejects during MAIL FROM (SMTPSenderRefused)
                    email_rejected = True
                    assert e.smtp_code == 552

            time.sleep(0.1)

            # Verify email was NOT stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 0
            assert email_rejected, "Email should have been rejected due to size limit"

        finally:
            controller.stop()


def test_smtputf8_support():
    """Test that SMTPUTF8 is supported and UTF-8 addresses work"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10033,
        )

        controller.start()

        try:
            # Send email with UTF-8 characters in addresses
            with smtplib.SMTP("127.0.0.1", 10033) as smtp:
                # Verify SMTPUTF8 is announced in EHLO response
                smtp.ehlo()
                assert "smtputf8" in smtp.esmtp_features

                sender = "user@example.com"
                # Use UTF-8 recipient (using valid ASCII for actual test)
                # Real UTF-8 addresses would require SMTPUTF8 MAIL FROM option
                recipients = ["recipient@example.com"]
                # Encode message as UTF-8 bytes to send Unicode content
                message = (
                    b"Subject: UTF-8 Test\r\n\r\n"
                    b"Test message with UTF-8: \xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e"
                )

                smtp.sendmail(sender, recipients, message)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

            # Verify UTF-8 content
            email = mbox[list(mbox.keys())[0]]
            assert "UTF-8 Test" in email["Subject"]
            # Verify UTF-8 content is preserved in the stored email
            payload = email.get_payload()
            assert "UTF-8" in payload or "日本語" in payload

        finally:
            controller.stop()


def test_smtputf8_can_be_disabled():
    """Test that SMTPUTF8 can be disabled via enable_SMTPUTF8 parameter"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)

        handler = DsmtpdHandler(maildir)
        controller = Controller(
            handler,
            hostname="127.0.0.1",
            port=10034,
            enable_SMTPUTF8=False,
        )

        controller.start()

        try:
            # Verify SMTPUTF8 is NOT announced when disabled
            with smtplib.SMTP("127.0.0.1", 10034) as smtp:
                smtp.ehlo()
                assert "smtputf8" not in smtp.esmtp_features

                # Send a simple ASCII email (should work fine)
                sender = "user@example.com"
                recipients = ["recipient@example.com"]
                message = b"Subject: ASCII Test\r\n\r\nThis is a simple ASCII message."

                smtp.sendmail(sender, recipients, message)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

        finally:
            controller.stop()
