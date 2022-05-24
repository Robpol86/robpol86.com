"""Generate static files from templates."""
import os
from typing import List

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder

FILES = [
    "robots.txt",
]


def create_files(app: Sphinx) -> List:
    """Create files and save to root of Sphinx outdir.

    Calling builder.handle_page() directly to access outfilename argument.

    :param app: Sphinx application.
    """
    builder: StandaloneHTMLBuilder = app.builder
    for template_name in FILES:
        page_name = os.path.splitext(template_name)[0]
        builder.handle_page(
            pagename=page_name,
            addctx={},
            templatename=template_name,
            # outfilename=template_name,
        )
    return []


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application.
    """
    app.connect("html-collect-pages", create_files)
