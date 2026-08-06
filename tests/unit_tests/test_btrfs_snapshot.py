"""Test btrfs-snapshot.sh."""

import base64
import os
import re
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

MOCK_BTRFS_OUTPUT_FILENAME = "btrfs_fake_output.txt"
MOCK_UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SNAPSHOTS_DIR = ".bsnaps"
SNAPSHOT_NAME = "test_name"


def run(argv, **kwargs) -> str:
    """Run btrfs-snapshot script with arguments passed to it.

    Output is converted to string and returned.
    """
    root = Path(__file__).parent / ".." / ".."
    snapshot_take_path = root / "docs" / "posts" / "2026" / "_static" / "btrfs-snapshot.sh"
    env = dict(os.environ, **kwargs.pop("env", {}))
    output = subprocess.check_output([snapshot_take_path] + argv, stderr=subprocess.STDOUT, env=env, **kwargs)  # noqa: S603
    return output.decode("utf8")


def run_failed(argv, **kwargs) -> str:
    """Call run() with expected failure and return the output."""
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run(argv, **kwargs)
    output = exc.value.output
    return output.decode("utf8")


def y64_encode(input) -> str:
    """Encode input string into Yahoo 64 format."""
    b64_encoded = base64.b64encode(input.encode("utf8")).decode("utf8")
    y64_encoded = b64_encoded.replace("+", ".").replace("/", "_").replace("=", "-")
    return y64_encoded


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
    fake_btrfs_script = dedent("""\
        #!/bin/bash
        set -eu
        if [[ "$*" == *"subvolume snapshot -r"* ]]; then
            intermediate="$(mktemp -d)/intermediate"
            cp -vr "${@:(-2):1}" "$intermediate"
            mv "$intermediate" "${@: -1}"
            echo "Create readonly snapshot of '${@:(-2):1}' in '${@: -1}'"
            exit 0
        fi
        if [[ "$*" == *"subvolume list"* ]]; then
            cat "$MOCK_BTRFS_OUTPUT_FILE"
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


@pytest.mark.parametrize("no_args", [True, False])
def test_cli_help_top(no_args: bool):
    """Test help output without subcommands."""
    if no_args:
        output = run([])
    else:
        output = run(["-h"])
    lines = output.splitlines()
    assert lines[0].startswith("Usage: ")
    assert lines[0].endswith("<command> [OPTIONS] [<args>]")
    assert lines[-1].startswith("more information on creating snapshots")


@pytest.mark.parametrize("subcommand", ["take", "create", "list", "ls", "restore", "delete", "revert", "undo"])
def test_cli_help_sub(subcommand: str):
    """Test help output for subcommands."""
    output = run([subcommand, "-h"])

    # Handle aliases, usage is static.
    if subcommand == "create":
        subcommand = "take"
    if subcommand == "ls":
        subcommand = "list"
    if subcommand == "undo":
        subcommand = "revert"

    assert re.match(f"^Usage: [a-zA-Z0-9_-]+ {subcommand}", output)
    lines = output.splitlines()
    assert lines[-1].startswith("  -v ")


def test_cli_bad_args():
    """Test script's handling of bad CLI arguments."""
    pytest.skip()  # TODO
    # getopts doesn't support long options. Provide guidance on common usage.
    output = run_failed(["--help"])
    assert "unknown option '--help'" in output

    output = run_failed(["unknown", "-h"])
    assert "unknown command 'unknown'" in output

    output = run_failed(["take", SNAPSHOT_NAME, "extra"])
    assert "requires exactly 1 argument" in output

    output = run_failed(["take", "-z", SNAPSHOT_NAME])
    assert "unknown flag: 'z'" in output

    output = run_failed(["take", "-c"])
    assert "flag needs an argument: 'c'" in output


def test_cli_overide_defaults():
    """Make sure Usage string replacement for displaying defaults works."""
    pytest.skip()  # TODO
    output = run(["take", "-s/altroot", "-h"])
    assert "Default: /altroot\n" in output


def test_take_sanity_checks(monkeypatch: pytest.MonkeyPatch, subvolume: Path):
    """Test sanity checks related to btrfs before making changes to the filesystem."""
    # Test not BTRFS.
    monkeypatch.setenv("MOCK_STAT_BIG_T", "fat32")
    output = run_failed(["take", "-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert "is not a btrfs filesystem." in output
    monkeypatch.delenv("MOCK_STAT_BIG_T")

    # Test not a subvolume.
    monkeypatch.setenv("MOCK_STAT_LITTLE_I", "123")
    output = run_failed(["take", "-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert "is not a btrfs subvolume." in output
    monkeypatch.delenv("MOCK_STAT_LITTLE_I")

    # Test snapshot already exists.
    snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / "0"
    snapshot_path.mkdir(parents=True)
    output = run_failed(["take", "-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert f"Snapshot '{snapshot_path}' already exists" in output


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
    output = run(["take", "-v", "-s", str(subvolume), SNAPSHOT_NAME])
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_take_comment(subvolume: Path):
    """Test creating snapshots with comments."""
    comment = "This is a test."
    encoded = y64_encode(comment)
    expected_snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / f"0{encoded}"
    assert not expected_snapshot_path.exists()

    # Run.
    output = run(["take", "-v", "-s", str(subvolume), "-c", comment, SNAPSHOT_NAME])
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_take_comment_multiline(subvolume: Path):
    """Test user comments from stdin."""
    comment = "Multiline\ncomment.\n"
    encoded = y64_encode(comment)
    expected_snapshot_path = subvolume / SNAPSHOTS_DIR / SNAPSHOT_NAME / f"0{encoded}"
    assert not expected_snapshot_path.exists()

    # Run.
    output = run(["take", "-v", "-s", str(subvolume), "-c-", SNAPSHOT_NAME], input=comment.encode("utf8"))
    assert f"Create readonly snapshot of '{subvolume}' in '{expected_snapshot_path}'" in output
    assert expected_snapshot_path.is_dir()


def test_list_no_snapshots(subvolume: Path, bin_dir: Path):
    """Test list with no snapshots."""
    mock_btrfs_output_file = bin_dir / MOCK_BTRFS_OUTPUT_FILENAME
    mock_btrfs_output_file.write_text(
        dedent("""\
        ID	gen	cgen	top level	otime	path
        --	---	----	---------	-----	----
    """)
    )

    # Run.
    env = dict(MOCK_BTRFS_OUTPUT_FILE=mock_btrfs_output_file)
    output = run_failed(["list", "-v", "-s", str(subvolume)], env=env)
    assert "No snapshots found." in output


def test_list_snapshots(subvolume: Path, bin_dir: Path):
    """Test listing snapshots."""
    mock_btrfs_output_file = bin_dir / MOCK_BTRFS_OUTPUT_FILENAME
    mock_btrfs_output_file.write_text(
        dedent(f"""\
        ID	gen	cgen	top level	otime	path
        --	---	----	---------	-----	----
        000	93	93	5		2026-07-29 13:00:00	snapshots/ignore-me
        111	93	93	5		2026-07-29 13:00:00	.bsnaps/one/0
        222	93	93	5		2026-07-29 14:00:00	.bsnaps/two/1
        333	93	93	5		2026-07-29 15:00:00	.bsnaps/three/0{y64_encode("Single line comment.")}
        444	93	93	5		2026-07-29 16:00:00	.bsnaps/four/0{y64_encode("Multi\nline\ncomment.")}
    """)
    )

    # Run.
    env = dict(MOCK_BTRFS_OUTPUT_FILE=mock_btrfs_output_file)
    output = run(["list", "-s", str(subvolume)], env=env)

    # Check.
    expected = dedent("""\
        ID   Date          Running? Name             Comment
        -------------------------------------------------------------------------------
        111  2026-07-29 13:00:00    one
        222  2026-07-29 14:00:00  * two
        333  2026-07-29 15:00:00    three            Single line comment.
        444  2026-07-29 16:00:00    four             Multi
                                                     line
                                                     comment.
    """)
    assert output == expected


def test_list_snapshots_no_comments(subvolume: Path, bin_dir: Path):
    """Test listing snapshots without any comments."""
    mock_btrfs_output_file = bin_dir / MOCK_BTRFS_OUTPUT_FILENAME
    mock_btrfs_output_file.write_text(
        dedent("""\
        ID	gen	cgen	top level	otime	path
        --	---	----	---------	-----	----
        111	93	93	5		2026-07-29 13:00:00	.bsnaps/one/0
        222	93	93	5		2026-07-29 14:00:00	.bsnaps/two/1
        333	93	93	5		2026-07-29 15:00:00	.bsnaps/three/0
        444	93	93	5		2026-07-29 16:00:00	.bsnaps/four/0
    """)
    )

    # Run.
    env = dict(MOCK_BTRFS_OUTPUT_FILE=mock_btrfs_output_file)
    output = run(["list", "-s", str(subvolume)], env=env)

    # Check.
    expected = dedent("""\
        ID   Date          Running? Name             Comment
        -------------------------------------------------------------------------------
        111  2026-07-29 13:00:00    one
        222  2026-07-29 14:00:00  * two
        333  2026-07-29 15:00:00    three
        444  2026-07-29 16:00:00    four
    """)
    assert output == expected


@pytest.mark.parametrize("medium", [True, False])
def test_list_snapshots_long_name(subvolume: Path, bin_dir: Path, medium: bool):
    """Test table with snapshots that have long names."""
    mock_btrfs_output_file = bin_dir / MOCK_BTRFS_OUTPUT_FILENAME
    if medium:
        mock_btrfs_output_file.write_text(
            dedent(f"""\
            ID	gen	cgen	top level	otime	path
            --	---	----	---------	-----	----
            111	93	93	5		2026-07-29 13:00:00	.bsnaps/one/0
            222	93	93	5		2026-07-29 14:00:00	.bsnaps/two/1
            333	93	93	5		2026-07-29 15:00:00	.bsnaps/snapshot-medium-name/0{y64_encode("Comment.")}
            444	93	93	5		2026-07-29 16:00:00	.bsnaps/four/0{y64_encode("Multi\nline\ncomment.")}
            """)
        )
    else:
        mock_btrfs_output_file.write_text(
            dedent(f"""\
            ID	gen	cgen	top level	otime	path
            --	---	----	---------	-----	----
            111	93	93	5		2026-07-29 13:00:00	.bsnaps/one/0
            222	93	93	5		2026-07-29 14:00:00	.bsnaps/two/1
            333	93	93	5		2026-07-29 15:00:00	.bsnaps/snapshot-a-very-long-name-indeed/0{y64_encode("Comment.")}
            444	93	93	5		2026-07-29 16:00:00	.bsnaps/four/0{y64_encode("Multi\nline\ncomment.")}
            """)
        )

    # Run.
    env = dict(MOCK_BTRFS_OUTPUT_FILE=mock_btrfs_output_file)
    output = run(["list", "-s", str(subvolume)], env=env)

    # Check.
    if medium:
        expected = dedent("""\
            ID   Date          Running? Name                  Comment
            -------------------------------------------------------------------------------
            111  2026-07-29 13:00:00    one
            222  2026-07-29 14:00:00  * two
            333  2026-07-29 15:00:00    snapshot-medium-name  Comment.
            444  2026-07-29 16:00:00    four                  Multi
                                                              line
                                                              comment.
        """)
    else:
        expected = dedent("""\
            ID   Date          Running? Name                            Comment
            -------------------------------------------------------------------------------
            111  2026-07-29 13:00:00    one
            222  2026-07-29 14:00:00  * two
            333  2026-07-29 15:00:00    snapshot-a-very-long-name-indeed  Comment.
            444  2026-07-29 16:00:00    four                            Multi
                                                                        line
                                                                        comment.
        """)
    assert output == expected
