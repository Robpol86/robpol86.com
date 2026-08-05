"""Test btrfs-snapshot.sh."""

import base64
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest

MOCK_BTRFS_OUTPUT_FILE = "btrfs_fake_output.txt"
MOCK_UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SNAPSHOTS_DIR = ".bsnaps"
SNAPSHOT_NAME = "test_name"


def run(argv, **kwargs) -> str:
    """Run btrfs-snapshot script with arguments passed to it.

    Output is converted to string and returned.
    """
    root = Path(__file__).parent / ".." / ".."
    snapshot_take_path = root / "docs" / "posts" / "2026" / "_static" / "btrfs-snapshot.sh"
    output = subprocess.check_output([snapshot_take_path] + argv, stderr=subprocess.STDOUT, **kwargs)  # noqa: S603
    return output.decode("utf8")


@pytest.fixture(autouse=True, name="bin_dir")
def _bin_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Create a bin directory and mock out shell commands for the happy path."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setenv("OLDPATH", os.environ["PATH"])
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)

    # macOS GNU alternatives (brew installed).
    if ggrep := shutil.which("ggrep"):
        (bin_dir / "grep").symlink_to(ggrep)
    if gsed := shutil.which("gsed"):
        (bin_dir / "sed").symlink_to(gsed)
    if gawk := shutil.which("gawk"):
        (bin_dir / "awk").symlink_to(gawk)
    if gcut := shutil.which("gcut"):
        (bin_dir / "cut").symlink_to(gcut)
    if gwc := shutil.which("gwc"):
        (bin_dir / "wc").symlink_to(gwc)

    # No-op mount and findmnt.
    if true_ := shutil.which("true"):
        (bin_dir / "mount").symlink_to(true_)
        (bin_dir / "findmnt").symlink_to(true_)
    else:
        raise RuntimeError

    # Mock stat.
    fake_stat_script = dedent("""\
        #!/bin/bash
        set -u
        if [[ "$*" == *"%T"* ]]; then
            echo "${MOCK_STAT_BIG_T:-btrfs}"
            exit 0
        fi
        if [[ "$*" == *"%i"* ]]; then
            echo "${MOCK_STAT_LITTLE_I:-256}"
            exit 0
        fi
        # macOS
        if command -v gstat &>/dev/null; then
            command gstat "$@"
        else
            export PATH="$OLDPATH"
            stat "$@"
        fi
    """)
    fake_stat = bin_dir / "stat"
    fake_stat.write_text(fake_stat_script)
    fake_stat.chmod(0o755)

    # Mock btrfs.
    fake_btrfs_output = bin_dir / MOCK_BTRFS_OUTPUT_FILE
    fake_btrfs_script = dedent(f"""\
        #!/bin/bash
        set -eu
        if [[ "$*" == *"subvolume snapshot -r"* ]]; then
            intermediate="$(mktemp -d)/intermediate"
            cp -vr "${{@:(-2):1}}" "$intermediate"
            mv "$intermediate" "${{@: -1}}"
            echo "Create readonly snapshot of '${{@:(-2):1}}' in '${{@: -1}}'"
            exit 0
        fi
        if [[ "$*" == *"subvolume list"* ]]; then
            [ -e "{fake_btrfs_output}" ] && cat "$_" || true
            exit 0
        fi
        exit 1
    """)
    fake_btrfs = bin_dir / "btrfs"
    fake_btrfs.write_text(fake_btrfs_script)
    fake_btrfs.chmod(0o755)

    # Mock UUID file for macOS.
    mock_uuid_file = tmp_path / "uuid.txt"
    mock_uuid_file.write_text(f"{MOCK_UUID}\n")
    monkeypatch.setenv("KERNEL_UUID_FILE", str(mock_uuid_file))

    return bin_dir


@pytest.fixture(name="subvolume")
def _subvolume(tmp_path: Path):
    """Create an empty directory to serve as a fake btrfs subvolume."""
    subvolume = tmp_path / "subvolume"
    subvolume.mkdir()
    return subvolume


def test_help():
    """Test script's handling of -h."""
    output = run(["-h"])
    lines = output.splitlines()
    assert lines[0].startswith("Usage: ")
    assert lines[-2].startswith("  -v ")
    assert lines[-1] == ""
    assert "Default: .bsnaps\n" in output
    assert "Default: /\n" in output


def test_bad_args():
    """Test script's handling of bad CLI arguments."""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run([])
    output = exc.value.output.decode("utf8")
    assert "requires exactly 1 argument" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["a", "b", "c"])
    output = exc.value.output.decode("utf8")
    assert "requires exactly 1 argument" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-z"])
    output = exc.value.output.decode("utf8")
    assert "unknown flag: 'z'" in output

    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-c"])
    output = exc.value.output.decode("utf8")
    assert "flag needs an argument: 'c'" in output


def test_overide_defaults():
    """Make sure Usage string replacement for displaying defaults works."""
    output = run(["-dSNAPSHOTS", "-s/altroot", "-h"])
    assert "Default: SNAPSHOTS\n" in output
    assert "Default: /altroot\n" in output


def test_take_sanity_checks(monkeypatch: pytest.MonkeyPatch, subvolume: Path):
    """Test sanity checks related to BTRFS before making changes to the filesystem."""
    # Test not BTRFS.
    monkeypatch.setenv("MOCK_STAT_BIG_T", "fat32")
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert "is not a BTRFS filesystem." in exc.value.output.decode("utf8")
    monkeypatch.delenv("MOCK_STAT_BIG_T")

    # Test not a subvolume.
    monkeypatch.setenv("MOCK_STAT_LITTLE_I", "123")
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert "is not a BTRFS subvolume." in exc.value.output.decode("utf8")
    monkeypatch.delenv("MOCK_STAT_LITTLE_I")

    # Test snapshot already exists.
    snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / "0"
    snapshot_path.mkdir(parents=True)
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert f"Snapshot '{snapshot_path}' already exists" in exc.value.output.decode("utf8")


@pytest.mark.parametrize("running", [False, True])
def test_take_happy_path(subvolume: Path, bin_dir: Path, running: bool):
    """Test creating a snapshot."""
    expected_snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / ("1" if running else "0")
    assert not expected_snapshot_path.exists()

    # Mock.
    if running:
        (bin_dir / "findmnt").unlink()
        assert (false_ := shutil.which("false"))
        (bin_dir / "findmnt").symlink_to(false_)

    # Run.
    output = run(["-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_take_comment(subvolume: Path):
    """Test creating snapshots with comments."""
    comment = "This is a test."
    encoded = base64.b64encode(comment.encode("utf8")).decode("utf8").replace("+", ".").replace("/", "_").replace("=", "-")
    expected_snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / f"0{encoded}"
    assert not expected_snapshot_path.exists()

    # Run.
    output = run(["-v", "-s", str(subvolume), "-c", comment, SNAPSHOT_NAME])
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_take_comment_multiline(subvolume: Path):
    """Test user comments from stdin."""
    comment = "Multiline\ncomment.\n"
    encoded = base64.b64encode(comment.encode("utf8")).decode("utf8").replace("+", ".").replace("/", "_").replace("=", "-")
    expected_snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / f"0{encoded}"
    assert not expected_snapshot_path.exists()

    # Run.
    output = run(["-v", "-s", str(subvolume), "-c-", SNAPSHOT_NAME], input=comment.encode("utf8"))
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_list_no_snapshots(subvolume: Path):
    """Test list with no snapshots."""
    # Run.
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(["-vl", "-s", str(subvolume)])
    assert "No snapshots found." in exc.value.output.decode("utf8")


def test_list_snapshots(subvolume: Path):
    """Test listing snapshots."""
    pytest.skip()  # TODO

    # Create mock snapshots.
    def create_mock_snapshot(date: datetime, uuid_letter: str, name: str, running: bool, comment: str):
        _snapshot_dir = subvolume / SNAPSHOTS_DIR / re.sub(r"[a-z]", uuid_letter, MOCK_UUID)
        _snapshot_dir.mkdir(parents=True)
        _snapshot_metadata = _snapshot_dir / ".snapshot.nfo"
        _snapshot_metadata.write_text(f":name:{name}\n:running:{str(running).lower()}\n:comment:{comment}\n:comment-end:\n")
        timestamp = date.timestamp()
        os.utime(_snapshot_metadata, (timestamp, timestamp))

    create_mock_snapshot(datetime.fromisoformat("2026-07-29 13:00:00"), "a", "one", False, "")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 14:00:00"), "b", "two", True, "")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 15:00:00"), "c", "three", False, "Single line comment.")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 16:00:00"), "d", "four", False, "-\nMulti\nline\ncomment.")

    # Run.
    output = run(["-l", "-s", str(subvolume)])

    # Check.
    expected = dedent("""\
        ID   Date          Running? Name              Comment
        -------------------------------------------------------------------------------
        111  2026-07-29 13:00:00    one
        222  2026-07-29 14:00:00  * two
        333  2026-07-29 15:00:00    three             Single line comment.
        444  2026-07-29 16:00:00    four              Multi
                                                      line
                                                      comment.
    """)
    assert output == expected


def test_list_snapshots_no_comments(subvolume: Path):
    """Test listing snapshots without any comments."""
    pytest.skip()

    # Run.
    output = run(["-l", "-s", str(subvolume)])

    # Check.
    expected = dedent("""\
        ID   Date          Running? Name
        -------------------------------------------------------------------------------
        111  2026-07-29 13:00:00    one
        222  2026-07-29 14:00:00  * two
        333  2026-07-29 15:00:00    three
        444  2026-07-29 16:00:00    four
    """)
    assert output == expected


@pytest.mark.parametrize("medium", [False, True])
def test_list_snapshots_long_name(subvolume: Path, medium: bool):
    """Test listing snapshots without any comments."""
    pytest.skip()

    # Run.
    output = run(["-l", "-s", str(subvolume)])

    # Check.
    if medium:  # TODO
        expected = dedent("""\
            ID   Date          Running? Name              Comment
            -------------------------------------------------------------------------------
            111  2026-07-29 13:00:00    one
            222  2026-07-29 14:00:00  * two
            333  2026-07-29 15:00:00    three             Single line comment.
            444  2026-07-29 16:00:00    four              Multi
                                                          line
                                                          comment.
        """)
    else:  # TODO
        expected = dedent("""\
            ID   Date          Running? Name              Comment
            -------------------------------------------------------------------------------
            111  2026-07-29 13:00:00    one
            222  2026-07-29 14:00:00  * two
            333  2026-07-29 15:00:00    three             Single line comment.
            444  2026-07-29 16:00:00    four              Multi
                                                          line
                                                          comment.
        """)
    assert output == expected
