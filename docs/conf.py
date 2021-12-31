"""Sphinx configuration file."""
# pylint: disable=invalid-name
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from sphinx.application import Sphinx

GIT_BRANCH = os.environ.get("SPHINX_GITHUB_BRANCH", "") or os.environ.get("GITHUB_REF", "").split("/", 2)[-1] or "main"
GIT_URL = "https://github.com/Robpol86/robpol86.com"


# General configuration.
copyright = f'{time.strftime("%Y")}, Robpol86'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io/en/latest/index.html
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_disqus.disqus",  # https://sphinx-disqus.readthedocs.io
    "sphinx_imgur.imgur",  # https://sphinx-imgur.readthedocs.io
    "sphinx_last_updated_by_git",  # https://github.com/mgeier/sphinx-last-updated-by-git
    "sphinx_panels",  # https://sphinx-panels.readthedocs.io
    "sphinx_sitemap",  # https://github.com/jdillard/sphinx-sitemap
    "sphinxcontrib.youtube",  # https://github.com/sphinx-contrib/youtube
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
language = "en"
project = "Robpol86.com"
pygments_style = "vs"
templates_path = ["_templates"]


# Options for HTML output.
html_baseurl = os.environ.get("SPHINX_HTML_BASEURL", "http://localhost:8000/")
html_context = {
    "edit_page_url_template": (
        "{{ github_url }}/{{ github_user }}/{{ github_repo }}/blob/{{ github_version }}/{{ doc_path }}{{ file_name }}"
    ),
}
html_copy_source = False
html_css_files = ["background_image.css", "fixes.css"]
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
        f'License: <a href="{GIT_URL}/blob/{GIT_BRANCH}/LICENSE">BSD-2-Clause</a><br>'
        "</p>"
    ),
    "logo_only": True,
    "path_to_docs": "docs",
    "repository_branch": GIT_BRANCH,
    "repository_url": GIT_URL,
    "use_edit_page_button": True,
}
html_title = "Robpol86.com"


# https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "linkify",
    "replacements",
    "substitution",
    "tasklist",
]
myst_substitutions = {
    "resume_link": f"[Résumé]({html_baseurl.rstrip('/')}/{html_static_path[0].strip('/')}/resume.pdf)",
}
myst_url_schemes = ["http", "https", "mailto"]


# https://sphinx-notfound-page.readthedocs.io/en/latest/configuration.html
notfound_context = dict(
    title="404 Not Found",
    body="<h1>404 Not Found</h1>\n\n"
    '<iframe src="https://funhtml5games.com?embed=lemmings" style="width:742px;height:401px;border:none;" '
    'frameborder="0" scrolling="no"></iframe>',
)
notfound_urls_prefix = ""


# https://sphinx-disqus.readthedocs.io/en/v1.2.0/install.html
disqus_shortname = "rob86wiki"


# https://sphinx-imgur.readthedocs.io/en/v3.0.0/usage.html
imgur_target_format = "https://i.imgur.com/%(id)s.%(ext)s"


# https://sphinx-panels.readthedocs.io/en/latest/#sphinx-configuration
panels_add_bootstrap_css = False


# https://github.com/jdillard/sphinx-sitemap#customizing-the-url-scheme
sitemap_url_scheme = "{link}"


# https://sphinxext-opengraph.readthedocs.io/en/latest/#options
ogp_site_url = html_baseurl
ogp_description_length = 300
ogp_image = f"{html_baseurl.rstrip('/')}/{html_logo.rsplit('.', 1)[0]}.png"
ogp_site_name = "Robpol86.com"
ogp_type = "website"
ogp_use_first_image = True
ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image">',
    f'<meta property="twitter:domain" content="{urlparse(html_baseurl).netloc}">',
]


# robots.txt templating
def render_robots_txt(app: Sphinx, _):
    """Parse Jinja2 templating in robots.txt file.

    :param app: Sphinx application object.
    :param _: Unused.
    """
    robots_txt_path = Path(app.outdir) / "robots.txt"
    if robots_txt_path.is_file():
        contents = robots_txt_path.read_text(encoding="utf8")
        context = dict(app.config.html_context, config=app.config)
        rendered = app.builder.templates.render_string(contents, context)
        robots_txt_path.write_text(rendered, encoding="utf8")


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.connect("build-finished", render_robots_txt)
