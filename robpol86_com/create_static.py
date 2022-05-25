"""Generate static files from templates."""
import os
from typing import List

from sphinx.application import Sphinx

FILES = [
    "robots.txt",
]


def create_files(app: Sphinx) -> List:
    """Create files and save to root of Sphinx outdir.

    Calling builder.handle_page() directly to access outfilename argument.

    :param app: Sphinx application.
    """
    builder = app.builder
    config = app.config
    outdir = app.outdir
    context = {
        "html_baseurl": config.html_baseurl,
    }
    for template_name in FILES:
        builder.handle_page(
            pagename="",
            addctx=context,
            templatename=template_name,
            outfilename=os.path.join(outdir, template_name),
        )
    return []


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application.
    """
    # app.connect("html-collect-pages", create_files)
