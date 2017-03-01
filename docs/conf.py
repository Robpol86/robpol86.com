"""Sphinx configuration file."""

import os
import time

from docutils import nodes
from docutils.parsers.rst import roles


# General configuration.
author = 'Robpol86'
copyright = '{}, {}'.format(time.strftime('%Y'), author)
html_last_updated_fmt = '%c {}'.format(time.tzname[time.localtime().tm_isdst])
master_doc = 'index'
project = 'Robpol86.com'
pygments_style = 'friendly'
suppress_warnings = ['image.nonlocal_uri']
templates_path = ['_templates']
extensions = list()


# Options for HTML output.
html_context = dict(
    conf_py_path='/docs/',
    display_github=True,
    github_repo=os.environ.get('TRAVIS_REPO_SLUG', '/' + project).split('/', 1)[1],
    github_user=os.environ.get('TRAVIS_REPO_SLUG', 'robpol86/').split('/', 1)[0],
    github_version=os.environ.get('TRAVIS_BRANCH', 'master'),
    source_suffix='.rst',
)
html_copy_source = False
html_extra_path = ['.htaccess', 'robots.txt']
html_favicon = 'favicon.ico'
html_theme = 'sphinx_rtd_theme'
html_title = project


# disqus
extensions.append('sphinxcontrib.disqus')
disqus_shortname = 'rob86wiki'


# google analytics
extensions.append('sphinxcontrib.googleanalytics')
googleanalytics_id = 'UA-30840244-1'


# imgur
extensions.append('sphinxcontrib.imgur')
imgur_client_id = '13d3c73555f2190'
imgur_target_default_gallery = True
imgur_target_default_page = True


# SCVersioning.
scv_grm_exclude = ('.gitignore',)
scv_show_banner = True


# GitHub rst inline roes.
def github_roles(name, rawtext, text, *_):
    """Handle several GitHub rst inline roles.

    :param str name: Role name (e.g. 'gh-repo').
    :param str rawtext: Entire role and value markup (e.g. ':gh-repo:`terminaltables`').
    :param str text: The parameter used in the role markup (e.g. 'terminaltables').

    :return: 2-item tuple of lists. First list are the rst nodes replacing the role. Second is a list of errors.
    :rtype: tuple
    """
    if name == 'gh-repo':
        node = nodes.reference(rawtext, text, refuri='https://github.com/Robpol86/' + text)
    else:
        kind = name[3:].lower()
        url = 'https://img.shields.io/github/{}/Robpol86/{}.svg?style=social'.format(kind, text)
        node = nodes.image(rawtext, uri=url)
    return [node], []
roles.register_canonical_role('gh-forks', github_roles)
roles.register_canonical_role('gh-repo', github_roles)
roles.register_canonical_role('gh-stars', github_roles)
roles.register_canonical_role('gh-watchers', github_roles)


def html_page_context(app, pagename, templatename, context, doctree):
    """Update the Jinja2 HTML context.

    :param sphinx.application.Sphinx app: Sphinx application object.
    :param str pagename: Name of the page being rendered (without .html or any file extension).
    :param str templatename: Page name with .html.
    :param dict context: Jinja2 HTML context.
    :param docutils.nodes.document doctree: Tree of docutils nodes.
    """
    # Disable `includehidden=True` from sphinx_rtd_theme.
    toctree = context['toctree']
    context['toctree'] = lambda **kwargs: toctree(**dict(kwargs, includehidden=False))


def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    app.connect('html-page-context', html_page_context)
