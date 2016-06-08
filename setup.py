#!/usr/bin/env python

import summarizer

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

readme = open('README.md').read()

setup(
    name='summarizer',
    version=summarizer.__version__,
    description='A Python utility for summarizing articles using nltk.',
    long_description=readme,
    author='rusad',
    author_email='bagration@list.ru',
    #url='https://github.com/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'nltk>=3.2',
        'beautifulsoup4>=4.4.1',
    ],
    zip_safe=False,
)

