"""Code mainly used in continuous integration."""
import os
from typing import Optional, Tuple


def git_url_branch() -> Tuple[Optional[str], Optional[str]]:
    """Determine the git URL and branch used for repo links."""
    if "GITHUB_REPOSITORY" in os.environ:
        # Running from GitHub Actions.
        url = f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}'
        if "SPHINX_GITHUB_BRANCH" in os.environ:
            # Apply override.
            branch = os.environ["SPHINX_GITHUB_BRANCH"]
        elif "GITHUB_BASE_REF" in os.environ:
            # In a pull request.
            branch = os.environ["GITHUB_SHA"]
        else:
            branch = os.environ["GITHUB_REF_NAME"]
    else:
        # Running locally, disable repo links.
        url = None
        branch = None

    return url, branch
