import os

import sphinx_rtd_theme


# General configuration.
author = 'Robpol86'
extensions = ['sphinxcontrib.disqus', 'sphinxcontrib.imgur']
master_doc = 'index'
nitpicky = True
project = 'Robpol86.com'
release = '1.0'
templates_path = ['_templates']
version = release


# Options for HTML output.
html_context = dict(
    conf_py_path='/docs/',
    display_github=True,
    github_repo=os.environ.get('TRAVIS_REPO_SLUG', '/robpol86.com').split('/', 1)[1],
    github_user=os.environ.get('TRAVIS_REPO_SLUG', 'selfcov/').split('/', 1)[0],
    github_version='master',
    source_suffix='.rst',
)
html_copy_source = False
html_extra_path = ['.htaccess', 'robots.txt']
html_favicon = 'favicon.ico'
html_last_updated_fmt = '%B %d, %Y'
html_show_copyright = False
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_title = project


# Options for extensions.
disqus_shortname = 'rob86wiki'
imgur_client_id = '13d3c73555f2190'
