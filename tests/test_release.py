import datetime
import importlib.util
from pathlib import Path

import pytest

_RELEASE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "release.py"
_spec = importlib.util.spec_from_file_location("release", _RELEASE_PATH)
release = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release)


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


def _changes_with_unreleased(bullets: str) -> str:
    return (
        "dsmtpd Changelog\n================\n\n"
        "Unreleased\n----------\n\n"
        f"{bullets}"
        "\nVersion 1.2.0\n-------------\n\n- old\n"
    )


def test_promote_unreleased(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(_changes_with_unreleased("- some change\n"))
    release.promote_unreleased("1.2.1", changes_path=changes, today=datetime.date(2026, 5, 7))
    out = changes.read_text()
    assert "Version 1.2.1\n-------------\n\nReleased on 2026-05-07." in out
    assert "Unreleased" not in out
    assert "Version 1.2.0" in out
    assert "- some change" in out


def test_promote_unreleased_missing_marker(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text("no unreleased section here\n")
    with pytest.raises(SystemExit, match="missing 'Unreleased' section"):
        release.promote_unreleased("1.2.1", changes_path=changes)


def test_promote_unreleased_empty_section_refused(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(_changes_with_unreleased(""))
    with pytest.raises(SystemExit, match="no bullet entries"):
        release.promote_unreleased("1.2.1", changes_path=changes)


def test_promote_unreleased_whitespace_only_section_refused(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(_changes_with_unreleased("\n\n  \n"))
    with pytest.raises(SystemExit, match="no bullet entries"):
        release.promote_unreleased("1.2.1", changes_path=changes)


def test_get_release_notes(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(
        "dsmtpd Changelog\n================\n\n"
        "Version 1.2.1\n-------------\n\n"
        "Released on 2026-05-07.\n\n"
        "- Drop ``aiosmtpd`` from build deps (#41)\n"
        "- Fix SMTPUTF8 test (#40)\n\n"
        "Version 1.2.0\n-------------\n\n"
        "- Old stuff\n"
    )
    notes = release.get_release_notes("1.2.1", changes_path=changes)
    assert notes.startswith("Released on 2026-05-07.")
    assert "(#41)" in notes
    assert "(#40)" in notes
    assert "Old stuff" not in notes
    assert "Version 1.2.0" not in notes


def test_get_release_notes_unknown_version(tmp_path):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(
        "dsmtpd Changelog\n================\n\nVersion 1.2.0\n-------------\n\n- foo\n"
    )
    assert release.get_release_notes("9.9.9", changes_path=changes) == ""


def test_main_atomicity_on_empty_unreleased(tmp_path, monkeypatch):
    """If promote_unreleased fails, __init__.py must NOT be modified."""
    init = tmp_path / "__init__.py"
    init.write_text('__version__ = "1.2.0"\n')
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(_changes_with_unreleased(""))
    monkeypatch.setattr(release, "INIT", init)
    monkeypatch.setattr(release, "CHANGES", changes)
    with pytest.raises(SystemExit, match="no bullet entries"):
        release.main("patch")
    assert '__version__ = "1.2.0"' in init.read_text(), (
        "__init__.py must not be bumped if CHANGES validation fails"
    )


def test_main_end_to_end(tmp_path, monkeypatch):
    init = tmp_path / "__init__.py"
    init.write_text('__version__ = "1.2.0"\n')
    changes = tmp_path / "CHANGES.rst"
    changes.write_text(_changes_with_unreleased("- something (#1)\n"))
    monkeypatch.setattr(release, "INIT", init)
    monkeypatch.setattr(release, "CHANGES", changes)
    assert release.main("patch") == "1.2.1"
    assert '__version__ = "1.2.1"' in init.read_text()
    assert "Version 1.2.1" in changes.read_text()


def test_cli_notes_subcommand(tmp_path, monkeypatch, capsys):
    changes = tmp_path / "CHANGES.rst"
    changes.write_text("Version 1.2.1\n-------------\n\nReleased on 2026-05-07.\n\n- foo (#1)\n")
    monkeypatch.setattr(release, "CHANGES", changes)
    rc = release._cli(["release.py", "notes", "1.2.1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Released on 2026-05-07." in out
    assert "- foo (#1)" in out


def test_cli_usage_error(capsys):
    rc = release._cli(["release.py"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "usage" in err
