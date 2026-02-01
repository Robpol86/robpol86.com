"""Tests."""

import logging
import re
import subprocess

from _pytest.monkeypatch import MonkeyPatch


def test_lock(monkeypatch: MonkeyPatch):
    """Verify lock file is up to date."""
    monkeypatch.delenv("UV_FROZEN")
    process = subprocess.run(["uv", "lock", "--check"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = process.stdout.decode("utf8")
    # If up to date:
    if process.returncode == 0:
        assert re.findall(r"Resolved \d+ packages? in", stdout)
        return
    # If out of date print helpful message
    matches = re.findall(r"The lockfile .+ needs to be updated", stdout)
    if matches:
        logging.getLogger(__name__).warning(matches[0])
        raise RuntimeError("Update lock file with: make relock")
    # If another error fail
    assert not stdout
