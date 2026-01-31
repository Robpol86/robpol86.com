"""Read the docs/_images/pictures git submodule branch name."""

import re
from configparser import ConfigParser

from sphinx.application import Sphinx
from sphinx.config import Config


# pylint: disable=unused-argument
def read_gitmodules(app: Sphinx, config: Config):
    """Read data from .gitmodules and inject it into the Sphinx config.

    :param app: Sphinx application object.
    :param config: Sphinx config.
    """
    # Read .gitmodules.
    parser = ConfigParser()
    parser.read(app.confdir.parent / ".gitmodules")
    section = 'submodule "docs/_images/pictures"'
    branch = parser[section]["branch"]
    url = parser[section]["url"]
    repo = re.sub(r"^https://github.com/(.+)\.git$", r"\1", url)
    if repo == url or not repo:
        raise ValueError("Did not substitute")

    # Update Sphinx config.
    thumb_image_target_format_substitutions: dict = config.thumb_image_target_format_substitutions
    thumb_image_target_format_substitutions.setdefault("SUBMODULE_REPO", repo)
    thumb_image_target_format_substitutions.setdefault("SUBMODULE_BRANCH", branch)


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("config-inited", read_gitmodules)
