# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GVasp'
copyright = '2022, Hui Zhou'
author = 'Hui Zhou'
version = '0.1.4.beta'
release = '0.1.4.beta'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

sys.path.insert(0, os.path.abspath('../../gvasp'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon', 'sphinxcontrib.inkscapeconverter']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

source_suffix = ['.rst', '.md', '.MD']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for Latex ---
latex_elements = {
    'extraclassoptions': 'openany,oneside',
}

# -- Options for Translate ---
language = 'en'
locale_dirs = ['../locales/']
