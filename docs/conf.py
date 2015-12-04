# -*- coding: utf-8 -*-

html_theme_options = {
    'logo': 'logo.jpg',
    'github_user': 'jdost',
    'github_repo': 'lazbot',
    'travis_button': True,
}

import sys
import os
import alabaster

sys.path.insert(0, os.path.abspath('../src'))
from lazbot import __version__, Lazbot
from lazbot.utils import build_namespace, load_plugins

app = build_namespace("app")
app.config = {}
app.bot = Lazbot("")

load_plugins("../src/plugins")

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'alabaster',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

default_role = 'ref'

# General information about the project.
project = u'La-Z-Bot'
copyright = u'2015, jdost'

version = __version__
release = __version__

exclude_patterns = ['build']
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
pygments_style = 'sphinx'
highlight_language = "python"

# html_title = None
# html_short_title = None
# html_logo = None
# html_favicon = None

html_static_path = ['static']
html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html"]
}
# html_additional_pages = {}
html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = True
htmlhelp_basename = 'Lazbotdoc'


latex_documents = [
    ('index', 'lazbot.tex', u'La-Z-Bot Documentation',
     u'jdost', 'manual'),
]

man_pages = [
    ('index', 'lazbot', u'La-Z-Bot Documentation',
     [u'jdost'], 1)
]

texinfo_documents = [
    ('index', 'Lazbot', u'La-Z-Bot Documentation',
     u'jdost', 'Lazbot', 'Pythonic slack bot framework',
     'Miscellaneous'),
]
