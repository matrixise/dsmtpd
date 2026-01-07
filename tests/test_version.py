"""Tests for version information."""

import subprocess
import sys

import dsmtpd


def test_version_flag():
    """Test that --version prints the version and exits successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "dsmtpd", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert dsmtpd.__version__ in result.stdout


def test_version_attribute():
    """Test that __version__ attribute exists and is a string."""
    assert hasattr(dsmtpd, "__version__")
    assert isinstance(dsmtpd.__version__, str)
    assert len(dsmtpd.__version__) > 0
