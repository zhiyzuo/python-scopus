# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

import pyscopus
VERSION = pyscopus.__version__

setup(
    name='pyscopus',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['test*', '_site']),
    packages=['pyscopus'],

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,

    description='A Python wrapper for Scopus API',

    # The project's main homepage.
    url='http://zhiyzuo.github.io/python-scopus/',
    download_url='https://github.com/zhiyzuo/python-scopus/tarball/' + VERSION,

    # Author details
    author='Zhiya Zuo',
    author_email='zhiyazuo@gmail.com',

    # Choose your license
    license='MIT',
    copyright = 'Copyright (c) 2016 Zhiya Zuo',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Education',
        'Topic :: Utilities',
        'Operating System :: MacOS',
        'Operating System :: Unix',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='scopus python api document retrieval information scholar academic',
)
