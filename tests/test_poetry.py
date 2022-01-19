"""Tests."""
import logging
import re
import subprocess


def test_lock():
    """Verify Poetry lock file is up to date.

    Remove after https://github.com/python-poetry/poetry/issues/453 is implemented.
    """
    output = subprocess.check_output(["poetry", "install", "--dry-run"]).strip()
    matches = re.findall(rb"^Warning: The lock file is not up to date .*$", output, re.MULTILINE)
    if matches:
        logging.getLogger(__name__).warning(matches[0])
        raise RuntimeError("Update lock file with: rm -f poetry.lock && make $_")
