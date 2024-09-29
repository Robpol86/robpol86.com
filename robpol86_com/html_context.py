"""Modify HTML context."""

from typing import Any

from ablog.blog import Blog
from docutils.nodes import document, title
from sphinx.application import Sphinx


def override_disqus_identifier(app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree: document):
    """Patch ablog's page_id method to return the page title instead of its URL path.

    Allows restoring old comments after migration to ablog.

    TODO: make a pull request to ablog allowing user to override page_id via :disqus_identifier: front matter.

    :param app: Sphinx application object.
    :param pagename: Name of the page being rendered (without .html or any file extension).
    :param templatename: Page name with .html.
    :param context: Jinja2 HTML context.
    :param doctree: Tree of docutils nodes.
    """
    if not doctree:
        return
    title_node = next(iter(doctree.traverse(title)), None)
    if not title_node:
        return
    page_title = title_node.astext()
    ablog: Blog = context["ablog"]
    ablog.page_id = lambda *_: page_title


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-page-context", override_disqus_identifier, priority=999)
