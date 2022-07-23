from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('_c_dos.pyx',language_level=3))