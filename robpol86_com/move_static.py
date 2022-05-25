"""Move static files at the end of the build."""
from pathlib import Path
from typing import Optional

from sphinx.application import Sphinx


def move_to_root(app: Sphinx, exc: Optional[Exception]):
    """Move static files from outdir/_static to outdir.

    :param app: Sphinx application.
    :param exc: If an exception occurred during the build.
    """
    if exc:
        return

    outdir = Path(app.outdir)
    static_paths = [outdir / p for p in app.config.html_static_path]
    files = app.config.robpol86_com_move_static_to_root

    for file_name in files:
        for static in static_paths:
            file_path = static / file_name
            if file_path.exists():
                target_path = outdir / file_name
                file_path.rename(target_path)
                break


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application.
    """
    app.add_config_value("robpol86_com_move_static_to_root", [], "html")
    app.connect("build-finished", move_to_root)
