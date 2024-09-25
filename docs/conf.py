"""Sphinx configuration file."""

import re
import time
from pathlib import Path

from sphinx import addnodes

from robpol86_com import __license__, __version__ as version


# General configuration.
author = "Robpol86"
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
exclude_patterns = ["_build"]
extensions = [
    "myst_parser",  # https://myst-parser.readthedocs.io
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "ablog",  # https://ablog.readthedocs.io/
]
language = "en"
project = "Robpol86.com"
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
templates_path = ["_templates"]


# Options for HTML output.
html_domain_indices = False
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"
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


# Ablog settings.
ablog_builder = "dirhtml"
ablog_website = "_website"
blog_title = "ABlog"
blog_baseurl = "https://ablog.readthedocs.io/"
blog_locations = {
    "Pittsburgh": ("Pittsburgh, PA", "https://en.wikipedia.org/wiki/Pittsburgh"),
    "San Fran": ("San Francisco, CA", "https://en.wikipedia.org/wiki/San_Francisco"),
    "Denizli": ("Denizli, Turkey", "https://en.wikipedia.org/wiki/Denizli"),
}
blog_languages = {
    "en": ("English", None),
    "nl": ("Nederlands", None),
    "zh_CN": ("Chinese", None),
}
blog_default_language = "en"
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
disqus_shortname = "https-ablog-readthedocs-io"
disqus_pages = True
fontawesome_link_cdn = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"


# Extension settings.
intersphinx_mapping = {  # TODO remove
    "python": ("https://docs.python.org/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
extlinks = {
    "wiki": ("https://en.wikipedia.org/wiki/%s", "%s"),
    "issue": ("https://github.com/sunpy/ablog/issues/%s", "issue %s"),
    "pull": ("https://github.com/sunpy/ablog/pull/%s", "pull request %s"),
}
rst_epilog = """
.. _Sphinx: http://sphinx-doc.org/
.. _Python: https://python.org
.. _Disqus: https://disqus.com/
.. _GitHub: https://github.com/sunpy/ablog
.. _PyPI: https://pypi.python.org/pypi/ablog
.. _Read The Docs: https://readthedocs.org/
.. _Alabaster: https://github.com/bitprophet/alabaster
"""


def parse_event(env, sig, signode):
    event_sig_re = re.compile(r"([a-zA-Z-]+)\s*\((.*)\)")
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(","):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    from sphinx.util.docfields import GroupedField

    app.connect("autodoc-process-docstring", cut_lines(4, what=["module"]))
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
    fdesc = GroupedField("parameter", label="Parameters", names=["param"], can_collapse=True)
    app.add_object_type("event", "event", "pair: %s; event", parse_event, doc_field_types=[fdesc])
