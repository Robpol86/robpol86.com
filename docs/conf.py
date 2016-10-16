"""Sphinx configuration file."""

import os
import time
from datetime import datetime


# General configuration.
author = 'Robpol86'
copyright = '{}, {}'.format(time.strftime('%Y'), author)
master_doc = 'index'
project = 'Robpol86.com'
pygments_style = 'friendly'
release = version = datetime.utcnow().strftime('%Y.%m.%d')
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
