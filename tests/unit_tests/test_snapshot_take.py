"""Test snapshot-take.sh."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def run_snapshot_take(argv) -> bytes:
    """Run snapshot-take script with arguments passed to it."""
    root = Path(__file__).parent / ".." / ".."
    snapshot_take_path = root / "docs" / "posts" / "2026" / "_static" / "snapshot-take.sh"
    return subprocess.check_output([snapshot_take_path] + argv, stderr=subprocess.STDOUT)  # noqa: S603


@pytest.fixture(autouse=True)
def setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Mock out environment and commands with fake scripts."""
    mock_bin_dir = tmp_path / "bin"
    mock_bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(mock_bin_dir), prepend=os.pathsep)

    # macOS GNU alternatives.
    if ggrep := shutil.which("ggrep"):
        (mock_bin_dir / "grep").symlink_to(ggrep)
    if gsed := shutil.which("gsed"):
        (mock_bin_dir / "sed").symlink_to(gsed)


def test_help_and_no_or_bad_args():
    """Test script's handling of -h and bad CLI arguments."""
    # Test -h.
    output = run_snapshot_take(["-h"])
    lines = output.splitlines()
    assert lines[0].startswith(b"Usage:")
    assert lines[-2].startswith(b"  -v ")
    assert lines[-1] == b""
