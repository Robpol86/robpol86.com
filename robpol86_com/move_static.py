"""Move static files at the end of the build."""

from pathlib import Path
from typing import Optional

from sphinx.application import Sphinx
from sphinx.util import logging


def move_to_root(app: Sphinx, exc: Optional[Exception]):
    """Move static files from html_static_path into outdir.

    :param app: Sphinx application.
    :param exc: If an exception occurred during the build.
    """
    if exc:
        return

    log = logging.getLogger(__name__)
    outdir = Path(app.outdir)
    static_paths = [outdir / p for p in app.config.html_static_path]
    files = app.config.robpol86_com_move_static_to_root

    for file_name in files:
        for static in static_paths:
            source_path = static / file_name
            target_path = outdir / file_name
            if target_path.exists() and not source_path.exists():
                break  # Already moved.
            if source_path.exists():
                source_path.rename(target_path)
                break
        else:
            log.warning("File not found in %r: %s", app.config.html_static_path, file_name)


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application.
    """
    app.add_config_value("robpol86_com_move_static_to_root", [], "html")
    app.connect("build-finished", move_to_root)
