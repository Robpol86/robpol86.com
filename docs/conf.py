"""Sphinx configuration file."""
# pylint: disable=invalid-name
import os
import time
from urllib.parse import urlparse

from robpol86_com import __license__, __version__ as version

GIT_BRANCH = os.environ.get("SPHINX_GITHUB_BRANCH", "") or os.environ.get("GITHUB_REF", "").split("/", 2)[-1] or None
GIT_URL = f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}' if os.environ.get("GITHUB_REPOSITORY", "") else None


# General configuration.
copyright = f'{time.strftime("%Y")}, Robpol86'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "robpol86_com.html_context",
    "robpol86_com.move_static",
    "robpol86_com.tags",
    "sphinx_carousel.carousel",  # https://sphinx-carousel.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_disqus.disqus",  # https://sphinx-disqus.readthedocs.io
    "sphinx_external_toc",  # https://sphinx-external-toc.readthedocs.io
    "sphinx_imgur.imgur",  # https://sphinx-imgur.readthedocs.io
    "sphinx_last_updated_by_git",  # https://github.com/mgeier/sphinx-last-updated-by-git
    "sphinx_sitemap",  # https://github.com/jdillard/sphinx-sitemap
    "sphinxcontrib.youtube",  # https://github.com/sphinx-contrib/youtube
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
language = "en"
project = "Robpol86.com"
pygments_style = "vs"
release = version
suppress_warnings = ["myst.strikethrough"]
templates_path = ["_templates"]


# Options for HTML output.
html_baseurl = os.environ.get("SPHINX_HTML_BASEURL", "") or "http://localhost:8000/"
html_context = {
    "edit_page_url_template": (
        "{{ github_url }}/{{ github_user }}/{{ github_repo }}/blob/{{ github_version }}/{{ doc_path }}{{ file_name }}"
    ),
    "html_baseurl": html_baseurl,
    "license": __license__,
}
html_copy_source = False
html_css_files = ["aside_margin.css", "background_image.css"]
html_extra_path = [
    ".htaccess",
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
    "logo_only": True,
    "path_to_docs": "docs",
    "repository_branch": GIT_BRANCH,
    "repository_url": GIT_URL,
    "use_download_button": False,
    "use_edit_page_button": not not GIT_URL,  # pylint: disable=unneeded-not
    "use_fullscreen_button": False,
}
html_title = project
html_use_index = True


# Linkcheck settings.
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
    r"https://[\w.]*mibsolution.one/#",
    r"https://media.vw.com/",  # All curls result in 403
    r"https://mega.nz/(file|folder)/\w+#",
    r"https://www.ecstuning.com/",  # All curls result in 403
    r"https://www.qnx.com/developers/docs/[\w.]+/#",
    r"https?://192.168.\d+.\d+/",
]
linkcheck_retries = 3
linkcheck_timeout = 5


# Extension settings.
carousel_show_buttons_on_top = True
carousel_show_captions_below = True
carousel_show_controls = True
carousel_show_indicators = True
carousel_show_shadows = True
disqus_shortname = "rob86wiki"
external_toc_path = ".toc.yml"
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
ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image">',
    f'<meta property="twitter:domain" content="{urlparse(html_baseurl).netloc}">',
]
ogp_description_length = 300
ogp_image = f"{html_baseurl.rstrip('/')}/{html_logo.rsplit('.', 1)[0]}.png"
ogp_site_name = html_title
ogp_site_url = html_baseurl
ogp_type = "website"
ogp_use_first_image = True
robpol86_com_move_static_to_root = [
    "robots.txt",
]
sitemap_url_scheme = "{link}"
