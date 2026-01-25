"""Read the pictures git submodule's branch name."""

from sphinx.application import Sphinx
from sphinx.config import Config


# pylint: disable=unused-argument
def read_gitmodules(app: Sphinx, config: Config):
    """Read data from .gitmodules and inject it into the Sphinx config.

    :param app: Sphinx application object.
    :param config: Sphinx config.
    """
    thumb_image_target_format_substitutions: dict = config.thumb_image_target_format_substitutions
    branch = "initial"  # TODO
    thumb_image_target_format_substitutions.setdefault("SUBMODULE_BRANCH", branch)


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("config-inited", read_gitmodules)
