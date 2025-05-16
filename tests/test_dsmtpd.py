from tempfile import TemporaryDirectory
from os import listdir

# at least tests the import
from dsmtpd._dsmtpd import DsmtpdHandler, create_maildir


def test_create_maildir():
    with TemporaryDirectory() as tempdir:
        maildir = f"{tempdir}/Maildir"
        with create_maildir(maildir):
            assert set(listdir(maildir)) == set(('cur', 'tmp', 'new'))
