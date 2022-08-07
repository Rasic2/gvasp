import sysconfig
from setuptools import setup, find_packages
from distutils.extension import Extension
from pathlib import Path

import pybind11
from Cython.Build import cythonize

setup(
    name='gvasp',
    version='0.0.1',
    license='GPL-3.0',
    author='hui_zhou',
    author_email='1051987201@qq.com',
    url='https://github.com/Rasic2/gvasp',
    description='A quick post-process for resolve or assistant the VASP calculations',
    long_description=Path("./README.md").read_text(),
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    packages=find_packages(),
    setup_requires=[
        'pybind11',
        'Cython'
    ],
    install_requires=[
        'pybind11',
        'Cython',
        'lxml',
        'matplotlib',
        'numpy',
        'pandas',
        'pymatgen',
        'pymatgen-analysis-diffusion',
        'pyyaml',
        'scipy'],
    ext_modules=cythonize([Extension(name='gvasp.lib.dos_cython', sources=['extension/dos_cython.pyx']),
                           Extension(name='gvasp.lib.file_bind', sources=['extension/file_bind.cpp',
                                                                          'extension/file_lib.cpp'])],
                          language_level=3),
    include_dirs=[sysconfig.get_config_var("INCLUDE"), pybind11.get_include()],
    include_package_data=True,
    package_data={"gvasp": ["*.json", "*.yaml", "INCAR"]},
    entry_points={'console_scripts': ['gvasp = gvasp.main:main']}
)
