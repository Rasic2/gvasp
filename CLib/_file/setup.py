from setuptools import setup, Extension

functions_module = Extension(
    name ='_file',
    sources = ['_file.cpp', '_lib.cpp'],
    include_dirs = ['D:\Anaconda\include', 'D:\Anaconda\Library\include'],
    extra_compile_args = ['/source-charset:utf-8'],

)

setup(ext_modules = [functions_module])

