"""Code mainly used in continuous integration."""
import os
from typing import Optional


def git_branch() -> Optional[str]:
    """Return the git branch for repo links."""
    if "SPHINX_GITHUB_BRANCH" in os.environ:
        # Overridden.
        return os.environ["SPHINX_GITHUB_BRANCH"]

    if pr_sha := os.environ.get("GITHUB_HEAD_REF", ""):
        # In a pull request.
        return pr_sha

    if branch := os.environ.get("GITHUB_REF_NAME", ""):
        return branch

    # Running locally, disable repo links.
    return None


def git_url() -> Optional[str]:
    """Return the base url for repo links."""
    if "GITHUB_REPOSITORY" in os.environ:
        # Running from GitHub Actions.
        return f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}'
    return None
