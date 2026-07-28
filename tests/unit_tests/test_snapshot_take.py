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


def test_help_args():
    """Test script's handling of -h and bad CLI arguments."""
    # Test -h.
    output = run_snapshot_take(["-h"])
    lines = output.splitlines()
    assert lines[0].startswith(b"Usage:")
    assert lines[-2].startswith(b"  -v ")
    assert lines[-1] == b""
    # assert b'\nDefault: snapshots\n' in output
    # assert b'\nDefault: /\n' in output

    # Test bad args.
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take([])
    assert b'requires exactly 1 argument' in exc.value.output
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(['a', 'b', 'c'])
    assert b'requires exactly 1 argument' in exc.value.output
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(['-z'])
    assert b"unknown flag: 'z'" in exc.value.output
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(['-c'])
    assert b"flag needs an argument: 'c'" in exc.value.output

    # Test override defaults.
    # TODO
