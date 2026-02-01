"""pytest fixtures."""

import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(autouse=True)
def uv_locked(monkeypatch: MonkeyPatch):
    """Tell uv to not automatically update lock file when run with `uv run ...`."""
    monkeypatch.setenv("UV_FROZEN", "true")
