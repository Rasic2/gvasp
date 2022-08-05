from setuptools import setup, find_packages

setup(
    name='QVasp',
    description='A quick post-process for resolve or assistant the VASP calculations',
    author='hui_zhou',
    version='0.0.1',
    python_requires='>=3.9',
    platforms="manylinux_x86_64",
    packages=find_packages(),
    install_requires=[
        'Cython',
        'matplotlib',
        'numpy',
        'pymatgen',
        'lxml',
    ],
    include_package_data=True,
    package_data={"QVasp": ["lib/*.so", "*.json", "*.yaml", "INCAR"]},
)
