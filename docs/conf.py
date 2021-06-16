"""Sphinx configuration file."""

# pylint: disable=invalid-name

import os
import time


# General configuration.
copyright = f'{time.strftime("%Y")}, Robpol86'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io/en/latest/index.html
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_disqus.disqus",  # https://sphinx-disqus.readthedocs.io
    "sphinx_last_updated_by_git",  # https://github.com/mgeier/sphinx-last-updated-by-git
    "sphinx_panels",  # https://sphinx-panels.readthedocs.io
    "sphinxcontrib.imgur",
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
project = "Robpol86.com"
pygments_style = "vs"
templates_path = ["_templates"]


# Options for HTML output.
html_extra_path = [
    ".htaccess",
    "robots.txt",
    # favicon
    "_static/android-chrome-192x192.png",
    "_static/android-chrome-512x512.png",
    "_static/apple-touch-icon-120x120.png",
    "_static/apple-touch-icon-152x152.png",
    "_static/apple-touch-icon-180x180.png",
    "_static/apple-touch-icon-60x60.png",
    "_static/apple-touch-icon-76x76.png",
    "_static/apple-touch-icon.png",
    "_static/browserconfig.xml",
    "_static/favicon-16x16.png",
    "_static/favicon-32x32.png",
    "_static/favicon.ico",
    "_static/mstile-144x144.png",
    "_static/mstile-150x150.png",
    "_static/mstile-310x150.png",
    "_static/mstile-310x310.png",
    "_static/mstile-70x70.png",
    "_static/safari-pinned-tab.svg",
    "_static/site.webmanifest",
]
html_logo = "_static/logo.svg"
html_static_path = ["_static"]
html_theme = "sphinx_book_theme"
html_theme_options = {
    "extra_navbar": (
        "<p>"
        'Generator: <a href="https://www.sphinx-doc.org/">Sphinx</a><br>'
        'Theme: <a href="https://sphinx-book-theme.readthedocs.io/">Sphinx Book Theme</a><br>'
        'Host: <a href="https://www.nearlyfreespeech.net/">NearlyFreeSpeech.NET</a><br>'
        "</p>"
    ),
    "google_analytics_id": "UA-30840244-1",  # https://pydata-sphinx-theme.readthedocs.io
    "path_to_docs": "docs",
    "repository_branch": os.environ.get("GITHUB_REF", "").split("/", 2)[-1] or "main",
    "repository_url": "https://github.com/Robpol86/robpol86.com",
    "use_edit_page_button": False,  # TODO https://github.com/pydata/pydata-sphinx-theme/issues/424
    "use_repository_button": True,
}
html_title = ""


# https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "linkify",
    "replacements",
    "substitution",
    "tasklist",
]
myst_url_schemes = ["http", "https", "mailto"]


# https://sphinx-notfound-page.readthedocs.io/en/latest/configuration.html
notfound_context = dict(
    title="404 Not Found",
    body="<h1>404 Not Found</h1>\n\n"
    "Believe it or not this page isn't at home. Please leave a message at the beep.<br>\n"
    "It must be gone, or it'd give a response. Where could it be? Believe it or not it's not home!",
)
notfound_urls_prefix = ""


# https://sphinx-disqus.readthedocs.io/en/v1.2.0/install.html
disqus_shortname = "rob86wiki"


# https://sphinx-panels.readthedocs.io/en/latest/#sphinx-configuration
panels_add_bootstrap_css = False


# https://github.com/Robpol86/sphinx-imgur
imgur_client_id = "13d3c73555f2190"
imgur_target_default_gallery = True
imgur_target_default_page = True


# https://sphinxext-opengraph.readthedocs.io/en/latest/#options
ogp_site_url = os.environ.get("OGP_SITE_URL", "")
ogp_description_length = 300
ogp_image = f"{ogp_site_url.rstrip('/')}/{html_logo}"
ogp_site_name = "Robpol86.com"
ogp_type = "article"
ogp_use_first_image = True
