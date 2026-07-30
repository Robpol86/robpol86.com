"""Test snapshot-take.sh."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest


def run_snapshot_take(argv, **kwargs) -> str:
    """Run snapshot-take script with arguments passed to it.

    Output is converted to string and returned.
    """
    root = Path(__file__).parent / ".." / ".."
    snapshot_take_path = root / "docs" / "posts" / "2026" / "_static" / "snapshot-take.sh"
    output = subprocess.check_output([snapshot_take_path] + argv, stderr=subprocess.STDOUT, **kwargs)  # noqa: S603
    return output.decode("utf8")


@pytest.fixture(autouse=True, name="bin_dir")
def _bin_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Create a bin directory and mock out shell commands for the happy path."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
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
            command stat "$@"
        fi
    """)
    fake_stat = bin_dir / "stat"
    fake_stat.write_text(fake_stat_script)
    fake_stat.chmod(0o755)

    # Mock btrfs.
    fake_btrfs_script = dedent("""\
        #!/bin/bash
        set -eu
        if [[ "$*" == *"subvolume snapshot"* ]]; then
            intermediate="$(mktemp -d)/intermediate"
            cp -vr "${@:(-2):1}" "$intermediate"
            mv "$intermediate" "${@: -1}"
            echo "Create readonly snapshot of '${@:(-2):1}' in '${@: -1}'"
            exit 0
        fi
        exit 1
    """)
    fake_btrfs = bin_dir / "btrfs"
    fake_btrfs.write_text(fake_btrfs_script)
    fake_btrfs.chmod(0o755)

    # Mock UUID file for macOS.
    mock_uuid_file = tmp_path / "uuid.txt"
    mock_uuid_file.write_text("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n")
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
    snapshot_name = "test_name"

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
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


@pytest.mark.parametrize("running", [False, True])
def test_metadata_file(subvolume: Path, bin_dir: Path, running: bool):
    """Test snapshot metadata file."""
    snapshots_dir = "snapshots"
    snapshot_name = "test_name"

    # Mock.
    if running:
        (bin_dir / "findmnt").unlink()
        assert (false_ := shutil.which("false"))
        (bin_dir / "findmnt").symlink_to(false_)

    # Run.
    output = run_snapshot_take(["-vp", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert "Create readonly snapshot " in output

    # Check.
    metadata_file = subvolume / snapshots_dir / snapshot_name / ".snapshot.nfo"
    metadata_file_contents = metadata_file.read_text()
    metadata_file_contents_expected = dedent(f"""\
        :running:{"true" if running else "false"}
        :comment:
        :comment-end:
    """)
    assert metadata_file_contents == metadata_file_contents_expected


def test_metadata_comment(subvolume: Path):
    """Test user comments in the snapshot metadata file.."""
    snapshots_dir = "snapshots"
    snapshot_name = "test_name"
    comment = "This is a test."

    # Run.
    output = run_snapshot_take(["-vp", "-d", snapshots_dir, "-s", str(subvolume), "-c", comment, snapshot_name])
    assert "Create readonly snapshot " in output

    # Check.
    metadata_file = subvolume / snapshots_dir / snapshot_name / ".snapshot.nfo"
    metadata_file_contents = metadata_file.read_text()
    metadata_file_contents_expected = dedent(f"""\
        :running:false
        :comment:{comment}
        :comment-end:
    """)
    assert metadata_file_contents == metadata_file_contents_expected


def test_metadata_comment_multiline(subvolume: Path):
    """Test user comments from stdin in the snapshot metadata file."""
    snapshots_dir = "snapshots"
    snapshot_name = "test_name"

    # Run.
    output = run_snapshot_take(
        ["-vp", "-d", snapshots_dir, "-s", str(subvolume), "-c-", snapshot_name],
        input="Multiline\ncomment.\n".encode("utf8"),
    )
    assert "Create readonly snapshot " in output

    # Check.
    metadata_file = subvolume / snapshots_dir / snapshot_name / ".snapshot.nfo"
    metadata_file_contents = metadata_file.read_text()
    metadata_file_contents_expected = dedent("""\
        :running:false
        :comment:-
        Multiline
        comment.
        :comment-end:
    """)
    assert metadata_file_contents == metadata_file_contents_expected


def test_stale_metadata_file(subvolume: Path):
    """Test handling when stale metadata file is present."""
    snapshots_dir = "snapshots"
    snapshot_name = "test_name"
    metadata_file = subvolume / ".snapshot.nfo"  # Stale file in subvolume from previous attempt.

    metadata_file.write_text("stale")
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-vp", "-d", snapshots_dir, "-s", str(subvolume), snapshot_name])
    assert f"Stale file '{metadata_file}' found." in exc.value.output.decode("utf8")


def test_list_snapshots_no_snapshots(subvolume: Path):
    """Test list with no snapshots."""
    snapshots_dir = "snapshots"

    # Run.
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run_snapshot_take(["-vl", "-d", snapshots_dir, "-s", str(subvolume)])
    assert "No snapshots found." in exc.value.output.decode("utf8")


def test_list_snapshots(subvolume: Path):
    """Test listing snapshots."""
    snapshots_dir = "snapshots"

    # Create mock snapshots.
    def create_mock_snapshot(date: datetime, name: str, running: bool, comment: str):
        _snapshot_dir = subvolume / snapshots_dir / name
        _snapshot_dir.mkdir(parents=True)
        _snapshot_metadata = _snapshot_dir / ".snapshot.nfo"
        _snapshot_metadata.write_text(f":running:{str(running).lower()}\n:comment:{comment}\n:comment-end:\n")
        timestamp = date.timestamp()
        os.utime(_snapshot_metadata, (timestamp, timestamp))

    create_mock_snapshot(datetime.fromisoformat("2026-07-29 13:00:00"), "one", False, "")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 14:00:00"), "two", True, "")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 15:00:00"), "three", False, "Single line comment.")
    create_mock_snapshot(datetime.fromisoformat("2026-07-29 16:00:00"), "four", False, "-\nMulti\nline\ncomment.")

    # Run.
    output = run_snapshot_take(["-l", "-d", snapshots_dir, "-s", str(subvolume)])

    # Check.
    pytest.skip()  # TODO
    expected = dedent("""\
        Date          Running? Name              Comment
        -------------------------------------------------------------------------------
        2026-07-29 13:00:00    one
        2026-07-29 14:00:00  * two
        2026-07-29 15:00:00    three             Single line comment.
        2026-07-29 16:00:00    four              Multi
                                                 line
                                                 comment.
    """)
    assert output == expected
