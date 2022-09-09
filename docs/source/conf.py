# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GVasp'
copyright = '2022, hui_zhou'
author = 'hui_zhou'
version = '0.0.3'
release = '0.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

sys.path.insert(0, os.path.abspath('../../gvasp'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

source_suffix = ['.rst', '.md', '.MD']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
