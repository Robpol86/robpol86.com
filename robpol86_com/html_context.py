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


def set_extra_navbar(app: Sphinx, __, ___, context: Dict, ____):
    """Set extra_navbar theme option.

    :param app: Sphinx application object.
    :param __: Unused.
    :param ___: Unused.
    :param context: HTML context.
    :param ____: Unused.
    """
    context["theme_extra_navbar"] = app.builder.templates.render("extra_navbar.html", context)


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("html-page-context", change_icon_tooltip, priority=999)
    app.connect("html-page-context", set_extra_navbar)
