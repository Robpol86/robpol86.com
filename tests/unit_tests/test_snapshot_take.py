"""Test snapshot-take.sh."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def run_snapshot_take(argv) -> str:
    """Run snapshot-take script with arguments passed to it.

    Output is converted to string and returned.
    """
    root = Path(__file__).parent / ".." / ".."
    snapshot_take_path = root / "docs" / "posts" / "2026" / "_static" / "snapshot-take.sh"
    output = subprocess.check_output([snapshot_take_path] + argv, stderr=subprocess.STDOUT)  # noqa: S603
    return output.decode("utf8")


@pytest.fixture(autouse=True, name="bin_dir")
def _bin_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Create a bin directory to mock out shell commands."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)

    # macOS GNU alternatives.
    if ggrep := shutil.which("ggrep"):
        (bin_dir / "grep").symlink_to(ggrep)
    if gsed := shutil.which("gsed"):
        (bin_dir / "sed").symlink_to(gsed)

    return bin_dir


@pytest.fixture(name="subvolume")
def _subvolume(tmp_path: Path):
    """Create an empty directory to serve as a fake btrfs subvolume."""
    subvolume = tmp_path / "subvolume"
    subvolume.mkdir()
    return subvolume


def test_help():
    """Test script's handling of -h."""
    output = run_snapshot_take(["-h"])
    lines = output.splitlines()
    assert lines[0].startswith("Usage: ")
    assert lines[-2].startswith("  -v ")
    assert lines[-1] == ""
    assert "Default: snapshots\n" in output
    assert "Default: /\n" in output


def test_bad_args():
    """Test script's handling of bad CLI arguments."""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take([])
    output = exc.value.output.decode("utf8")
    assert "requires exactly 1 argument" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["a", "b", "c"])
    output = exc.value.output.decode("utf8")
    assert "requires exactly 1 argument" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-z"])
    output = exc.value.output.decode("utf8")
    assert "unknown flag: 'z'" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-c"])
    output = exc.value.output.decode("utf8")
    assert "flag needs an argument: 'c'" in output


def test_overide_defaults():
    """Make sure Usage string replacement for displaying defaults works."""
    output = run_snapshot_take(["-dSNAPSHOTS", "-s/altroot", "-h"])
    assert "Default: SNAPSHOTS\n" in output
    assert "Default: /altroot\n" in output


def test_btrfs_sanity_checks(subvolume, bin_dir):
    """Test sanity checks related to BTRFS before making changes to the filesystem."""
    snapshots_dir = "snapshots"
    snapshot_name = "name"

    # Test not BTRFS.
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert "is not a BTRFS filesystem." in exc.value.output.decode("utf8")

    # Test not a subvolume.
    fake_stat_script = '#!/bin/bash\n[[ "$*" == *"%T"* ]] && echo btrfs\n'
    fake_stat = (bin_dir / "stat")
    fake_stat.write_text(fake_stat_script)
    fake_stat.chmod(0o755)
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert "is not a BTRFS subvolume." in exc.value.output.decode("utf8")
    fake_stat_script += '[[ "$*" == *"%i"* ]] && echo 256\n'
    fake_stat.write_text(fake_stat_script)  # Greenlight for subsequent checks.

    # Test snapshot already exists.
    (subvolume / snapshots_dir / snapshot_name).mkdir(parents=True)
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert f"Snapshot '{snapshot_name}' already exists" in exc.value.output.decode("utf8")
