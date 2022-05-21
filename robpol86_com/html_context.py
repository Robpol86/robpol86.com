"""Modify HTML context."""
from typing import Dict, List

from sphinx.application import Sphinx


def change_icon_tooltip(_, __, ___, context: Dict, ____):
    """Change edit button icon and tooltip.

    https://github.com/executablebooks/sphinx-book-theme/blob/v0.3.2/src/sphinx_book_theme/header_buttons/__init__.py

    :param _: Unused.
    :param __: Unused.
    :param ___: Unused.
    :param context: HTML context.
    :param ____: Unused.
    """
    header_buttons: List[Dict[str, str]] = context.get("header_buttons", [])
    for button in header_buttons:
        if button["tooltip"] == "Edit this page":
            button["icon"] = "fab fa-github"
            button["tooltip"] = "View page source"


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-page-context", change_icon_tooltip, priority=999)
