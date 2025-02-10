"""Sphinx configuration file."""

# pylint: disable=invalid-name
import os
import time
from urllib.parse import urlparse

GIT_BRANCH = os.environ.get("SPHINX_GITHUB_BRANCH", "") or os.environ.get("GITHUB_REF_NAME", None)
GIT_URL = f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}' if os.environ.get("GITHUB_REPOSITORY", "") else None


# General configuration.
author = "Robpol86"
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
exclude_patterns = ["_build"]
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_imgur.imgur",  # https://sphinx-imgur.readthedocs.io
    "sphinx_sitemap",  # https://sphinx-sitemap.readthedocs.io
    "sphinxcontrib.youtube",  # https://sphinxcontrib-youtube.readthedocs.io
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
    "ablog",  # https://ablog.readthedocs.io/
    "robpol86_com.html_context",
]
language = "en"
project = "Robpol86.com"
pygments_style = "vs"
version = "1.0.0"
release = version
templates_path = ["_templates"]


# Options for HTML output.
html_baseurl = os.environ.get("SPHINX_HTML_BASEURL", "") or "http://localhost:8000/"
html_context = {
    "default_mode": "light",
    "html_baseurl": html_baseurl,
}
html_copy_source = False
html_css_files = ["aside_margin.css"]
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
    "analytics": {"google_analytics_id": "G-EJSD449CRH"},
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
linkcheck_exclude_documents = []
linkcheck_ignore = [
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
sitemap_url_scheme = "{link}"


# Ablog settings.
blog_authors = {"Robpol86": ("Robert Pooley", "https://robpol86.com")}
blog_baseurl = html_baseurl
blog_default_language = language
blog_feed_archives = False
blog_languages = {"en": ("English", None)}
blog_locations = {
    "Austin": ("Austin", "https://en.wikipedia.org/wiki/Austin,_Texas"),
    "Manhattan": ("Manhattan", "https://en.wikipedia.org/wiki/Manhattan"),
    "San Francisco": ("San Francisco", "https://en.wikipedia.org/wiki/San_Francisco"),
    "Victoria": ("Victoria", "https://en.wikipedia.org/wiki/Victoria,_Texas"),
    "Tokyo": ("Tokyo", "https://en.wikipedia.org/wiki/Tokyo"),
    "Hong Kong": ("Hong Kong", "https://en.wikipedia.org/wiki/Hong_Kong"),
    "Mexico City": ("Mexico City", "https://en.wikipedia.org/wiki/Mexico_City"),
    "Santiago": ("Santiago", "https://en.wikipedia.org/wiki/Santiago"),
}
blog_title = project
disqus_pages = False
disqus_shortname = "rob86wiki"
