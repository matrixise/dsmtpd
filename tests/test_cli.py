import sys
from unittest import mock
from unittest.mock import patch

from dsmtpd._dsmtpd import parse_args

def test_directory():
    args = ["dsmtpd", "-d", "maildir"]
    with patch.object(sys, 'argv', args):
        opts = parse_args()

        assert opts.directory == 'maildir'

def test_default_port():
    args = ["dsmtpd"]
    with patch.object(sys, 'argv', args):
        opts = parse_args()

        assert opts.port == 1025

def test_default_interface():
    args = ["dsmtpd"]
    with patch.object(sys, 'argv', args):
        opts = parse_args()

        assert opts.interface == "127.0.0.1"