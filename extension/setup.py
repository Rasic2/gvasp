import os
import shutil
from distutils.core import setup, Extension

from Cython.Build import cythonize

_file_module = Extension(name='_file', sources=['_file/_file.cpp', '_file/_lib.cpp'],
                         include_dirs=['/home/hzhou/anaconda3/include', '/home/hzhou/anaconda3/Library/include'])

setup(ext_modules=cythonize('_dos/_dos.pyx', language_level=3))
setup(ext_modules=[_file_module])

shutil.rmtree("build")
