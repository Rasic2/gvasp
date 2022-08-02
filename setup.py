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
        'Cython==0.29.31',
        'matplotlib',
        'numpy==1.23.1',
        'pymatgen==2022.7.25',
        'lxml==4.9.1',
    ],
    include_package_data=True,
    package_data={"QVasp": ["lib/*.so", "*.json", "*.yaml", "INCAR"]},
)
