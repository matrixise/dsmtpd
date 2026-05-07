#!/usr/bin/env python3
"""Bump dsmtpd version and promote the Unreleased section in CHANGES.rst.

Usage:
    python scripts/release.py {patch|minor|major}

Side effects:
    - dsmtpd/__init__.py: ``__version__`` is updated.
    - CHANGES.rst: the ``Unreleased`` section becomes ``Version X.Y.Z``,
      dated today (ISO format).

Output (stdout):
    The new version, e.g. ``1.2.1``.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "dsmtpd" / "__init__.py"
CHANGES = ROOT / "CHANGES.rst"

VERSION_RE = re.compile(r'^__version__ = "(\d+)\.(\d+)\.(\d+)"$', re.MULTILINE)
UNRELEASED_MARKER = "Unreleased\n----------"


def bump(current: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = current
    if part == "major":
        return (major + 1, 0, 0)
    if part == "minor":
        return (major, minor + 1, 0)
    if part == "patch":
        return (major, minor, patch + 1)
    raise SystemExit(f"unknown version part: {part!r} (expected: patch|minor|major)")


def current_version(*, init_path: Path = INIT) -> tuple[int, int, int]:
    m = VERSION_RE.search(init_path.read_text())
    if not m:
        raise SystemExit(f"could not find __version__ in {init_path}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def update_init(new_version: str, *, init_path: Path = INIT) -> None:
    text = init_path.read_text()
    if not VERSION_RE.search(text):
        raise SystemExit(f"could not find __version__ in {init_path}")
    init_path.write_text(VERSION_RE.sub(f'__version__ = "{new_version}"', text, count=1))


def promote_unreleased(
    new_version: str,
    *,
    changes_path: Path = CHANGES,
    today: datetime.date | None = None,
) -> None:
    text = changes_path.read_text()
    if UNRELEASED_MARKER not in text:
        raise SystemExit(f"missing 'Unreleased' section in {changes_path}")
    when = (today or datetime.date.today()).isoformat()
    title = f"Version {new_version}"
    new_section = f"{title}\n{'-' * len(title)}\n\nReleased on {when}."
    changes_path.write_text(text.replace(UNRELEASED_MARKER, new_section, 1))


def main(part: str) -> str:
    new = bump(current_version(), part)
    new_version = f"{new[0]}.{new[1]}.{new[2]}"
    update_init(new_version)
    promote_unreleased(new_version)
    return new_version


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} {{patch|minor|major}}")
    print(main(sys.argv[1]))
