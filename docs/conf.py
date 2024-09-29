"""Sphinx configuration file."""

# pylint: disable=invalid-name
import os
import time

from robpol86_com import __license__, __version__ as version

GIT_BRANCH = os.environ.get("SPHINX_GITHUB_BRANCH", "") or os.environ.get("GITHUB_REF_NAME", None)
GIT_URL = f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}' if os.environ.get("GITHUB_REPOSITORY", "") else None


# General configuration.
author = "Robpol86"
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
exclude_patterns = ["_build"]
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_imgur.imgur",  # https://sphinx-imgur.readthedocs.io
    "sphinx_sitemap",  # https://sphinx-sitemap.readthedocs.io
    "sphinxcontrib.youtube",  # https://sphinxcontrib-youtube.readthedocs.io
    "ablog",  # https://ablog.readthedocs.io/
    "robpol86_com.html_context",
]
language = "en"
project = "Robpol86.com"
pygments_style = "vs"
release = version
templates_path = ["_templates"]


# Options for HTML output.
html_baseurl = os.environ.get("SPHINX_HTML_BASEURL", "") or "http://localhost:8000/"
html_context = {
    "default_mode": "dark",
    "html_baseurl": html_baseurl,
}
html_copy_source = False
html_extra_path = [
    ".htaccess",
]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.svg"
html_show_sourcelink = True
html_sidebars = {
    "**": [
        "navbar-logo.html",
        "search-button-field.html",
        "ablog_sbt_postcard.html",
        "ablog_sbt_recentposts.html",
        "ablog_sbt_tagcloud.html",
        "ablog_sbt_categories.html",
        "ablog_sbt_archives.html",
        "ablog_sbt_locations.html",
    ],
}
html_static_path = ["_static"]
html_theme = "sphinx_book_theme"
html_theme_options = {
    "path_to_docs": "docs",
    "repository_branch": GIT_BRANCH,
    "repository_url": GIT_URL,
    "use_download_button": False,
    "use_fullscreen_button": False,
    "use_source_button": not not GIT_URL,  # pylint: disable=unneeded-not
}
html_title = project
html_use_index = True


# Linkcheck settings.
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0"
linkcheck_allowed_redirects = {
    r"https://www.amazon.com/": "https://www.amazon.com/[^/]+/dp/",
    r"https://www.apc.com/us/en/product/\w+$": "https://www.apc.com/us/en/product/",
    r"https://www.mcmaster.com/": "https://www.mcmaster.com/ShellHomepageRefresh[.]aspx[?]searchTerm=",
    r"https://www.reddit.com/r/": r"https://www.reddit.com/r/.*?rdt=[\d]+",
    r"https://youtu.be/\w+$": "https://www.youtube.com/watch[?]",
}
linkcheck_exclude_documents = [
    # TODO remove all
    "atrix_lapdock",
    "bareos_tape_backup",
    "flash_droid_cricket",
    "raspberry_pi_luks",
    "raspberry_pi_project_fi",
    "rns_510_vim",
    "root_certificate_authority",
    "wireless_charging_car_dock",
]
linkcheck_ignore = [
    r"[/.]*genindex.html",  # TODO remove this
    r"https://[\w.]*mibsolution.one/",
    r"https://media.vw.com/",  # All curls result in 403
    r"https://mega.nz/(file|folder)/\w+#",
    r"https://parts.vw.com/",  # Nondeterministic rate limiting in GitHub runner
    r"https://torkliftcentral.com/",
    r"https://www.apc.com/",
    r"https://www.ecstuning.com/",  # All curls result in 403
    r"https://www.howardforums.com/",
    r"https://www.qnx.com/developers/docs/[\w.]+/#",
    r"https://www.reddit.com/",
    r"https?://192.168.\d+.\d+/",
]
linkcheck_retries = 3
linkcheck_timeout = 5


# Extension settings.
imgur_target_format = "https://i.imgur.com/%(id)s.%(ext)s"
myst_enable_extensions = ["colon_fence", "deflist", "fieldlist", "linkify", "replacements", "strikethrough", "substitution"]
myst_url_schemes = ("http", "https", "mailto")
notfound_context = dict(  # pylint: disable=use-dict-literal
    title="404 Not Found",
    body="<h1>404 Not Found</h1>\n\n"
    '<iframe src="https://funhtml5games.com?embed=lemmings" style="width:742px;height:401px;border:none;" '
    'frameborder="0" scrolling="no"></iframe>',
)
notfound_urls_prefix = ""
sitemap_url_scheme = "{link}"


# Ablog settings.
ablog_builder = "dirhtml"
ablog_website = "_website"
blog_title = project
blog_baseurl = html_baseurl
blog_locations = {
    "Pittsburgh": ("Pittsburgh, PA", "https://en.wikipedia.org/wiki/Pittsburgh"),
    "San Fran": ("San Francisco, CA", "https://en.wikipedia.org/wiki/San_Francisco"),
    "Denizli": ("Denizli, Turkey", "https://en.wikipedia.org/wiki/Denizli"),
}
blog_languages = {
    "en": ("English", None),
}
blog_default_language = language
blog_authors = {
    "Ahmet": ("Ahmet Bakan", "https://ahmetbakan.com"),
    "Luc": ("Luc Saffre", "https://saffre-rumma.net/luc/"),
    "Mehmet": ("Mehmet Gerçeker", "https://github.com/mehmetg"),
}
blog_feed_archives = True
blog_feed_fulltext = True
blog_feed_templates = {
    "atom": {
        "content": "{{ title }}{% for tag in post.tags %} #{{ tag.name|trim()|replace(' ', '') }} {% endfor %}",
    },
    "social": {
        "content": "{{ title }}{% for tag in post.tags %} #{{ tag.name|trim()|replace(' ', '') }} {% endfor %}",
    },
}
disqus_shortname = "rob86wiki"
disqus_pages = False
fontawesome_link_cdn = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"


"""
TODOs:
* Decide upon tags and categories for all my pages
* Ensure post dates are accurrate
* convert imgur-embed into list-table of figures
* closely look at diffs of all pages and visually check in pc and mobile browsers
* Confirm all pages keep the same URLs as main branch
* split up photo albums into independent posts, link to them in the original page
* Revisit conf.py
* Revisit pyproject.toml
* Revisit GitHub Actions
* log 404s and confirm me visiting bad pages logs correctly
* robots.txt
* apple favicons
* revisit all extension settings here
* fix imgur-embed in latest sphinx
* validate rss
* fix tags having too much whitespace with commas
* html validator, ogp validator
* fontawsome conflict? ablog and maybe sbt both use it
"""
