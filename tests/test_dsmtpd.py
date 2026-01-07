import asyncio
import mailbox
from os import listdir
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

# at least tests the import
from dsmtpd._dsmtpd import DsmtpdHandler, create_maildir, ensure_maildir, is_maildir


def test_create_maildir():
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        with create_maildir(maildir):
            assert set(listdir(maildir)) == set(("cur", "tmp", "new"))


def test_ensure_maildir_creates_new():
    """Test ensure_maildir creates a new Maildir when path doesn't exist"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        ensure_maildir(maildir)
        assert is_maildir(maildir)
        assert set(listdir(maildir)) == set(("cur", "tmp", "new"))


def test_ensure_maildir_repairs_existing():
    """Test ensure_maildir repairs a Maildir with missing subdirectories"""
    with TemporaryDirectory() as tempdir:
        import os

        maildir = f"{tempdir}/Maildir"
        os.makedirs(maildir)
        os.makedirs(f"{maildir}/cur")  # Only create 'cur', missing 'tmp' and 'new'

        ensure_maildir(maildir)
        assert is_maildir(maildir)
        assert set(listdir(maildir)) == set(("cur", "tmp", "new"))


def test_is_maildir_valid():
    """Test is_maildir returns True for valid Maildir"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        with create_maildir(maildir):
            assert is_maildir(maildir) is True


def test_is_maildir_invalid():
    """Test is_maildir returns False for invalid Maildir"""
    with TemporaryDirectory() as tempdir:
        assert is_maildir(tempdir) is False


def test_handler_initialization():
    """Test that DsmtpdHandler can be initialized"""
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        handler = DsmtpdHandler(maildir)
        assert handler is not None


def test_handle_data_with_bytes():
    """Test handle_DATA with bytes content (Python 3.13+)"""

    async def run_test():
        with TemporaryDirectory() as tempdir:
            maildir = f"{tempdir}/Maildir"
            ensure_maildir(maildir)

            handler = DsmtpdHandler(maildir)

            # Mock server and session
            server = Mock()
            session = Mock()
            session.peer = ("127.0.0.1", 12345)

            # Mock envelope with bytes content
            envelope = Mock()
            envelope.mail_from = "sender@example.com"
            envelope.rcpt_tos = ["recipient@example.com"]
            envelope.content = b"Subject: Test Email\n\nThis is a test email body."

            # Call handle_DATA
            result = await handler.handle_DATA(server, session, envelope)

            # Verify the result is '250 OK' (success)
            assert result == "250 OK"

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

    asyncio.run(run_test())


def test_handle_data_with_string():
    """Test handle_DATA with string content (older Python versions)"""

    async def run_test():
        with TemporaryDirectory() as tempdir:
            maildir = f"{tempdir}/Maildir"
            ensure_maildir(maildir)

            handler = DsmtpdHandler(maildir)

            # Mock server and session
            server = Mock()
            session = Mock()
            session.peer = ("127.0.0.1", 54321)

            # Mock envelope with string content
            envelope = Mock()
            envelope.mail_from = "sender@test.com"
            envelope.rcpt_tos = ["user1@test.com", "user2@test.com"]
            envelope.content = "Subject: String Test\n\nThis is a test with string content."

            # Call handle_DATA
            result = await handler.handle_DATA(server, session, envelope)

            # Verify the result is '250 OK' (success)
            assert result == "250 OK"

            # Verify email was stored
            mbox = mailbox.Maildir(maildir, create=False)
            assert len(mbox) == 1

    asyncio.run(run_test())


def test_handle_data_logging():
    """Test that handle_DATA logs the correct information"""

    async def run_test():
        with TemporaryDirectory() as tempdir:
            maildir = f"{tempdir}/Maildir"
            ensure_maildir(maildir)

            handler = DsmtpdHandler(maildir)

            # Mock server and session
            server = Mock()
            session = Mock()
            session.peer = ("192.168.1.1", 9999)

            # Mock envelope
            envelope = Mock()
            envelope.mail_from = "test@example.org"
            envelope.rcpt_tos = ["dest@example.org"]
            envelope.content = b"Subject: Logging Test\n\nTest body."

            # Patch the logger to verify logging
            with patch("dsmtpd._dsmtpd.log") as mock_log:
                await handler.handle_DATA(server, session, envelope)

                # Verify log.info was called with the expected format
                assert mock_log.info.called
                call_args = mock_log.info.call_args
                assert "192.168.1.1:9999" in str(call_args)
                assert "test@example.org" in str(call_args)
                assert "dest@example.org" in str(call_args)

    asyncio.run(run_test())
