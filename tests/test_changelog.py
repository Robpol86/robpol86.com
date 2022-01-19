"""Tests."""
import re
from pathlib import Path

from _pytest.fixtures import FixtureRequest


def test_changelog(request: FixtureRequest):
    """Verify changelog formatting for recent entries."""
    changelog = Path(__file__).parent.parent / "CHANGELOG.md"
    handle = changelog.open("r")
    request.addfinalizer(handle.close)

    # Verify "Unreleased" section.
    seen_unreleased = False
    for line in handle:
        if line == "## [Unreleased]\n":
            seen_unreleased = True
            break
    assert seen_unreleased

    # Validate most recent release section.
    seen_released = False
    for line in handle:
        if line.startswith("## "):
            assert re.findall(r"^## \d{4}-\d{2}-\d{2}\n$", line, re.MULTILINE)
            seen_released = True
            break
    assert seen_released

    # Validate release entry.
    line = handle.readline()
    assert line == "\n"  # Next line should be empty.
    line = handle.readline()
    assert 1 < len(line) <= 81  # Title line should be at most 80 characters including newline.
    line = handle.readline()
    assert line == "\n"  # Next line should also be empty.
    # Body is optional, not validating.
