from setuptools import setup, Extension

functions_module = Extension(
    name='_file',
    sources=['_file.cpp', '_lib.cpp'],
    include_dirs=['/home/hzhou/anaconda3/include', '/home/hzhou/anaconda3/Library/include'],

)

setup(ext_modules=[functions_module])
