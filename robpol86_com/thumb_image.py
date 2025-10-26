"""TODO.

https://sphinx-thumb_image.readthedocs.io
https://github.com/Robpol86/sphinx-thumb_image
https://pypi.org/project/sphinx-thumb_image
"""

from typing import Dict

from docutils.parsers.rst import directives
from docutils.parsers.rst.directives import images
from sphinx.application import Sphinx

DEFAULT_SCALE_WIDTH = 700
DEFAULT_TARGET_FORMAT = "https://media.githubusercontent.com/media/Robpol86/robpol86.com/refs/heads/no-imgur/docs/%(img)s"


class ThumbImage(images.Image):
    """Thumbnail image directive."""

    option_spec = images.Image.option_spec.copy()
    option_spec["scale_width"] = directives.unchanged  # TODO
    option_spec["target_format"] = directives.unchanged  # TODO


class ThumbFigure(images.Figure):
    """Thumbnail figure directive."""

    option_spec = images.Figure.option_spec.copy()
    option_spec["scale_width"] = directives.unchanged  # TODO


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application object.

    :returns: Extension version.
    """
    app.add_config_value("thumb_image_default_scale_width", DEFAULT_SCALE_WIDTH, "html")
    app.add_config_value("thumb_image_default_target_format", DEFAULT_TARGET_FORMAT, "html")
    app.add_directive("thumb-image", ThumbImage)
    app.add_directive("thumb-figure", ThumbFigure)
    return {"version": "0.0.1"}
