"""Test snapshot-take.sh."""

import os
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

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
    """Create a bin directory and mock out shell commands for the happy path."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)

    # macOS GNU alternatives.
    if ggrep := shutil.which("ggrep"):
        (bin_dir / "grep").symlink_to(ggrep)
    if gsed := shutil.which("gsed"):
        (bin_dir / "sed").symlink_to(gsed)

    # No-op mount and findmnt.
    if true_ := shutil.which("true"):
        (bin_dir / "mount").symlink_to(true_)
        (bin_dir / "findmnt").symlink_to(true_)
    else:
        raise RuntimeError

    # Mock stat.
    fake_stat_script = dedent("""\
        #!/bin/bash
        set -ux
        [[ "$*" == *"%T"* ]] && echo "${MOCK_STAT_BIG_T:-btrfs}"
        [[ "$*" == *"%i"* ]] && echo "${MOCK_STAT_LITTLE_I:-256}"
        exit 0
    """)
    fake_stat = bin_dir / "stat"
    fake_stat.write_text(fake_stat_script)
    fake_stat.chmod(0o755)

    # Mock btrfs.
    fake_btrfs_script = dedent("""\
        #!/bin/bash
        set -eux
        if [[ "$*" == *"subvolume snapshot"* ]]; then
            mkdir "${@: -1}"
            exit 0
        fi
        exit 1
    """)
    fake_btrfs = bin_dir / "btrfs"
    fake_btrfs.write_text(fake_btrfs_script)
    fake_btrfs.chmod(0o755)

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


def test_btrfs_sanity_checks(monkeypatch: pytest.MonkeyPatch, subvolume: Path):
    """Test sanity checks related to BTRFS before making changes to the filesystem."""
    snapshots_dir = "snapshots"
    snapshot_name = "name"

    # Test not BTRFS.
    monkeypatch.setenv("MOCK_STAT_BIG_T", "fat32")
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert "is not a BTRFS filesystem." in exc.value.output.decode("utf8")
    monkeypatch.delenv("MOCK_STAT_BIG_T")

    # Test not a subvolume.
    monkeypatch.setenv("MOCK_STAT_LITTLE_I", "123")
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert "is not a BTRFS subvolume." in exc.value.output.decode("utf8")
    monkeypatch.delenv("MOCK_STAT_LITTLE_I")

    # Test snapshot parent directory not exists.
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert f"Snapshots directory '{subvolume / snapshots_dir}' does not exist." in exc.value.output.decode("utf8")

    # Test snapshot already exists.
    (subvolume / snapshots_dir / snapshot_name).mkdir(parents=True)
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert f"Snapshot '{snapshot_name}' already exists" in exc.value.output.decode("utf8")


@pytest.mark.parametrize("parents_create", [True, False])
def test_happy_path(subvolume: Path, parents_create: bool):
    """Test creating a snapshot."""
    snapshots_dir = "snapshots"
    if not parents_create:
        (subvolume / snapshots_dir).mkdir()
    snapshot_name = "test_name"
    expected_snapshot_path = subvolume / snapshots_dir / snapshot_name
    assert not expected_snapshot_path.exists()

    # Run.
    output = run_snapshot_take(
        (["-p"] if parents_create else []) + ["-v", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name]
    )
    assert f"Created snapshot {expected_snapshot_path}\n" in output
    assert expected_snapshot_path.is_dir()


@pytest.mark.parametrize("running", [False, True])
def test_metadata_file(running: bool):
    """TODO."""
    pytest.skip()


def test_bad_metadata_file():
    """TODO."""
    pytest.skip()


def test_list_snapshots():
    """TODO."""
    pytest.skip()
