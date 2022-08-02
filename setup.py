from setuptools import setup, find_packages

setup(
    name='QVasp',
    packages=find_packages(),
    version='0.0.1',
    install_requires=[
        'Cython==0.29.31',
        'matplotlib',
        'numpy==1.23.1',
        'pymatgen==2022.7.25',
    ],
)
