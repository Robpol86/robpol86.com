"""Generate static files from templates."""
from pathlib import Path
from typing import Dict

from sphinx.application import Sphinx

FILES = [
    "robots.txt",
]


def create_files(app: Sphinx, __, ___, context: Dict, ____):
    """Create files and save to root of Sphinx outdir.

    :param app: Sphinx application object.
    :param __: Unused.
    :param ___: Unused.
    :param context: HTML context.
    :param ____: Unused.
    """
    outdir = app.outdir
    for file_name in FILES:
        rendered = app.builder.templates.render(file_name, context)
        target = Path(outdir) / file_name
        target.write_text(rendered, encoding="utf8")


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-page-context", create_files)  # TODO this runs on every page!
