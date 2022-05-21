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


def parse_extra_navbar(app: Sphinx, __, ___, context: Dict, ____):
    """Parse Jinja2 in extra_navbar theme option.

    :param app: Sphinx application object.
    :param __: Unused.
    :param ___: Unused.
    :param context: HTML context.
    :param ____: Unused.
    """
    theme_extra_navbar: str = context.get("theme_extra_navbar", "")
    if theme_extra_navbar:
        context["theme_extra_navbar"] = app.builder.templates.render_string(theme_extra_navbar, context)


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-page-context", change_icon_tooltip, priority=999)
    app.connect("html-page-context", parse_extra_navbar)
