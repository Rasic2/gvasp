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

setup(
    name='gvasp',
    version='0.1.2',
    license='GPL-3.0',
    author='hui_zhou',
    author_email='1051987201@qq.com',
    url='https://github.com/Rasic2/gvasp',
    description='A quick post-process for resolve or assistant the VASP calculations',
    long_description=Path("./README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        'pybind11',
        'Cython',
        'lxml',
        'matplotlib',
        'numpy',
        'pandas',
        'pyyaml',
        'scipy',
        'pytest',
        'seekpath'],
    ext_modules=cythonize([Extension(name='gvasp.lib.dos_cython', sources=['extension/dos_cython.pyx']),
                           Extension(name='gvasp.lib.path_cython', sources=['extension/path_cython.pyx'])],
                          language_level=3) +
                [Extension(name='gvasp.lib.file_bind', sources=['extension/file_bind.cpp',
                                                                'extension/file_lib.cpp']),
                 Extension(name='gvasp.lib.base_bind', sources=['extension/base_bind.cpp'])],
    include_dirs=[sysconfig.get_config_var("INCLUDE"), np.get_include(), pybind11.get_include()],
    include_package_data=True,
    package_data={"gvasp": ["*.json", "*.yaml", "INCAR", "*.submit", "*.sh"]},
    entry_points={'console_scripts': ['gvasp = gvasp.main:main']}
)
