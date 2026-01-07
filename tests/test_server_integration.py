"""
Integration tests for the SMTP server
"""
from tempfile import TemporaryDirectory
import smtplib
import time
import mailbox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            hostname='127.0.0.1',
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
            hostname='127.0.0.1',
            port=10026,
        )

        controller.start()

        try:
            # Send an email using smtplib
            with smtplib.SMTP('127.0.0.1', 10026) as smtp:
                sender = 'sender@example.com'
                recipients = ['recipient@example.com']
                message = 'Subject: Test Email\n\nThis is a test message.'

                smtp.sendmail(sender, recipients, message)

            # Give the server a moment to write the file
            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

            # Verify email content
            email = mbox[list(mbox.keys())[0]]
            assert email['Subject'] == 'Test Email'
            assert 'This is a test message.' in email.get_payload()

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
            hostname='127.0.0.1',
            port=10027,
        )

        controller.start()

        try:
            # Create a multipart message
            msg = MIMEMultipart()
            msg['From'] = 'test@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Multipart Test'

            body = 'This is the email body'
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            with smtplib.SMTP('127.0.0.1', 10027) as smtp:
                smtp.send_message(msg)

            time.sleep(0.1)

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

            # Verify email content
            email = mbox[list(mbox.keys())[0]]
            assert email['Subject'] == 'Multipart Test'
            assert email['From'] == 'test@example.com'
            assert email['To'] == 'recipient@example.com'

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
            hostname='127.0.0.1',
            port=10028,
        )

        controller.start()

        try:
            # Send email to multiple recipients
            with smtplib.SMTP('127.0.0.1', 10028) as smtp:
                sender = 'sender@example.com'
                recipients = [
                    'recipient1@example.com',
                    'recipient2@example.com',
                    'recipient3@example.com'
                ]
                message = 'Subject: Multiple Recipients Test\n\nTest message.'

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
            hostname='127.0.0.1',
            port=10029,
        )

        controller.start()

        try:
            # Send multiple emails
            with smtplib.SMTP('127.0.0.1', 10029) as smtp:
                for i in range(5):
                    sender = f'sender{i}@example.com'
                    recipients = [f'recipient{i}@example.com']
                    message = f'Subject: Test Email {i}\n\nMessage number {i}.'
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
            hostname='127.0.0.1',
            port=test_port,
        )

        controller.start()

        try:
            # Verify server is listening on the correct port
            actual_port = controller.server.sockets[0].getsockname()[1]
            assert actual_port == test_port

            # Send a test email
            with smtplib.SMTP('127.0.0.1', test_port) as smtp:
                smtp.sendmail(
                    'test@example.com',
                    ['dest@example.com'],
                    'Subject: Port Test\n\nTesting custom port.'
                )

            time.sleep(0.1)

            # Verify email was received
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

        finally:
            controller.stop()
