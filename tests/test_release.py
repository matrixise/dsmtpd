import datetime
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts import release  # noqa: E402


@pytest.mark.parametrize(
    "part,expected",
    [
        ("patch", (1, 2, 1)),
        ("minor", (1, 3, 0)),
        ("major", (2, 0, 0)),
    ],
)
def test_bump(part, expected):
    assert release.bump((1, 2, 0), part) == expected


def test_bump_unknown_part():
    with pytest.raises(SystemExit, match="unknown version part"):
        release.bump((1, 2, 0), "tweak")


def test_current_version(tmp_path):
    init = tmp_path / "__init__.py"
    init.write_text('"""docstring"""\n__version__ = "1.2.0"\n')
    assert release.current_version(init_path=init) == (1, 2, 0)


def test_current_version_missing(tmp_path):
    init = tmp_path / "__init__.py"
    init.write_text("# no version here\n")
    with pytest.raises(SystemExit, match="could not find __version__"):
        release.current_version(init_path=init)


def test_update_init(tmp_path):
    init = tmp_path / "__init__.py"
    init.write_text('"""docstring"""\n__version__ = "1.2.0"\n')
    release.update_init("1.2.1", init_path=init)
    assert '__version__ = "1.2.1"' in init.read_text()


def test_update_init_missing_marker(tmp_path):
    init = tmp_path / "__init__.py"
    init.write_text("# no version here\n")
    with pytest.raises(SystemExit, match="could not find __version__"):
        release.update_init("1.2.1", init_path=init)


def test_promote_unreleased(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(
        "dsmtpd Changelog\n================\n\n"
        "Unreleased\n----------\n\n- some change\n\n"
        "Version 1.2.0\n-------------\n\n- old\n"
    )
    release.promote_unreleased("1.2.1", changes_path=changes, today=datetime.date(2026, 5, 7))
    out = changes.read_text()
    assert "Version 1.2.1\n-------------\n\nReleased on 2026-05-07." in out
    assert "Unreleased" not in out
    assert "Version 1.2.0" in out


def test_promote_unreleased_missing_marker(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text("no unreleased section here\n")
    with pytest.raises(SystemExit, match="missing 'Unreleased' section"):
        release.promote_unreleased("1.2.1", changes_path=changes)
