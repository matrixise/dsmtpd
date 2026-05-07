#!/usr/bin/env python3
"""Bump dsmtpd version, promote CHANGES.rst, and extract release notes.

Usage:
    python scripts/release.py {patch|minor|major}
        Bump the version, promote the ``Unreleased`` section of
        ``CHANGES.rst`` to ``Version X.Y.Z`` dated today (ISO format), and
        print the new version on stdout.

    python scripts/release.py notes VERSION
        Print the body (everything between the section header and the next
        ``Version`` heading or end-of-file) of the section ``Version
        VERSION`` from ``CHANGES.rst``. Used to feed a richer commit message.

Side effects of the bump command:
    - dsmtpd/__init__.py: ``__version__`` is updated.
    - CHANGES.rst: the ``Unreleased`` section becomes ``Version X.Y.Z``.

The bump command refuses to proceed if the ``Unreleased`` section does
not exist or contains no bullet (``- ``) entry — releasing an empty
changelog section is almost always a mistake.
"""

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "dsmtpd" / "__init__.py"
CHANGES = ROOT / "CHANGES.rst"

VERSION_RE = re.compile(r'^__version__ = "(\d+)\.(\d+)\.(\d+)"$', re.MULTILINE)
UNRELEASED_MARKER = "Unreleased\n----------"
NEXT_SECTION_RE = re.compile(r"\nVersion ", re.MULTILINE)
BULLET_RE = re.compile(r"^- ", re.MULTILINE)


def bump(current: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if part == "major":
        return (major + 1, 0, 0)
    if part == "minor":
        return (major, minor + 1, 0)
    if part == "patch":
        return (major, minor, patch + 1)
    raise SystemExit(f"unknown version part: {part!r} (expected: patch|minor|major)")


def current_version(*, init_path: Path | None = None) -> tuple[int, int, int]:
    init_path = init_path if init_path is not None else INIT
    m = VERSION_RE.search(init_path.read_text())
    if not m:
        raise SystemExit(f"could not find __version__ in {init_path}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def update_init(new_version: str, *, init_path: Path | None = None) -> None:
    init_path = init_path if init_path is not None else INIT
    text = init_path.read_text()
    if not VERSION_RE.search(text):
        raise SystemExit(f"could not find __version__ in {init_path}")
    init_path.write_text(VERSION_RE.sub(f'__version__ = "{new_version}"', text, count=1))


def _section_body(text: str, header: str) -> tuple[int, int] | None:
    """Return (start, end) of the body following ``header`` in ``text``.

    The body starts right after the underline that follows the title and ends
    at the next ``\\nVersion `` marker or end of file. Returns ``None`` if the
    header is not present.
    """
    marker = header
    idx = text.find(marker)
    if idx == -1:
        return None
    body_start = idx + len(marker)
    next_match = NEXT_SECTION_RE.search(text, body_start)
    body_end = next_match.start() if next_match else len(text)
    return (body_start, body_end)


def promote_unreleased(
    new_version: str,
    *,
    changes_path: Path | None = None,
    today: datetime.date | None = None,
) -> None:
    changes_path = changes_path if changes_path is not None else CHANGES
    text = changes_path.read_text()
    span = _section_body(text, UNRELEASED_MARKER)
    if span is None:
        raise SystemExit(f"missing 'Unreleased' section in {changes_path}")
    body = text[span[0] : span[1]]
    if not BULLET_RE.search(body):
        raise SystemExit(
            f"'Unreleased' section in {changes_path} contains no bullet entries; "
            "refusing to release an empty changelog"
        )
    when = (today or datetime.date.today()).isoformat()
    title = f"Version {new_version}"
    new_section = f"{title}\n{'-' * len(title)}\n\nReleased on {when}."
    changes_path.write_text(text.replace(UNRELEASED_MARKER, new_section, 1))


def get_release_notes(version: str, *, changes_path: Path | None = None) -> str:
    """Return the body of the ``Version VERSION`` section in ``CHANGES.rst``."""
    changes_path = changes_path if changes_path is not None else CHANGES
    text = changes_path.read_text()
    title = f"Version {version}"
    underline = "-" * len(title)
    header = f"{title}\n{underline}"
    span = _section_body(text, header)
    if span is None:
        return ""
    return text[span[0] : span[1]].strip()


def main(part: str) -> str:
    new = bump(current_version(), part)
    new_version = f"{new[0]}.{new[1]}.{new[2]}"
    promote_unreleased(new_version)
    update_init(new_version)
    return new_version


def _cli(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "notes":
        print(get_release_notes(argv[2]))
        return 0
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        sys.stderr.write(f"usage: {argv[0]} {{patch|minor|major}} | notes VERSION\n")
        return 2
    print(main(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
