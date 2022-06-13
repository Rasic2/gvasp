from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('c_doscar_load.pyx',language_level=3))