import sysconfig

from setuptools import setup, find_packages
from distutils.extension import Extension
from pathlib import Path

import numpy as np
import pybind11
from Cython.Build import cythonize

if "win" in sysconfig.get_platform():
    # fix the Win error: LNK2001 PyInit_*
    from distutils.command.build_ext import build_ext


    def get_export_symbols_fixed(self, ext):
        pass


    build_ext.get_export_symbols = get_export_symbols_fixed

extra_compile_args = ["-std=c++11"] if "macosx" in sysconfig.get_platform() else []

setup(
    url='https://github.com/Rasic2/gvasp',
    long_description=Path("./README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["tests", "tests.*", "project", "project.*"]),
    ext_modules=cythonize([Extension(name='gvasp.lib.dos_cython', sources=['extension/dos_cython.pyx']),
                           Extension(name='gvasp.lib.path_cython', sources=['extension/path_cython.pyx'])],
                          language_level=3) +
                [Extension(name='gvasp.lib.file_bind', sources=['extension/file_bind.cpp',
                                                                'extension/file_lib.cpp'],
                           extra_compile_args=extra_compile_args),
                 Extension(name='gvasp.lib.base_bind', sources=['extension/base_bind.cpp'],
                           extra_compile_args=extra_compile_args)],
    include_dirs=[sysconfig.get_config_var("INCLUDE"), np.get_include(), pybind11.get_include()],
    include_package_data=True,
    package_data={"gvasp": ["*.json", "*.yaml", "INCAR", "*.submit", "*.sh"]}
)
