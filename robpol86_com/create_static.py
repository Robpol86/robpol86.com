"""Generate static files from templates."""
import os
from typing import Dict, List, Tuple

from sphinx.application import Sphinx

FILES = [
    "robots.txt",
]


def create_files(_) -> List[Tuple[str, Dict, str]]:
    """Create files and save to root of Sphinx outdir.

    :return: Page name, supplemental Jinja2 context, and template file name.
    """
    return [(os.path.splitext(f)[0], {}, f) for f in FILES]


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-collect-pages", create_files)
