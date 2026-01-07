import sys
from unittest.mock import patch

from dsmtpd._dsmtpd import parse_args


def test_directory():
    args = ["dsmtpd", "-d", "maildir"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.directory == "maildir"


def test_default_port():
    args = ["dsmtpd"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.port == 1025


def test_default_interface():
    args = ["dsmtpd"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.interface == "127.0.0.1"


def test_custom_port():
    """Test that custom port can be specified"""
    args = ["dsmtpd", "--port", "2525"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.port == 2525


def test_custom_max_size():
    """Test that custom max-size can be specified"""
    args = ["dsmtpd", "--max-size", "1048576"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.max_size == 1048576


def test_max_size_zero():
    """Test that max-size can be set to 0 (no limit)"""
    args = ["dsmtpd", "--max-size", "0"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.max_size == 0


def test_default_max_size():
    """Test that default max-size is 32 MiB"""
    args = ["dsmtpd"]
    with patch.object(sys, "argv", args):
        opts = parse_args()

        assert opts.max_size == 33554432  # 32 * 1024 * 1024
