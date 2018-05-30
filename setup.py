#!/usr/bin/python3

import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

setup(
    name="ripple-filter",
    version="0.1",
    description="Ripple detection classes, taken from Kemere Lab implementation",
    long_description=
    """This package contains classes meant for ripple detection. It is taken directly from 
    the Kemere Lab's C++ implementation [1]. 
    It contains classes for: 
    - ripple filter (bandwidth + lowpass filter), implemented in c for speed
    - mean/sd calculation classes
    - ripple detector class
    [1] https://www.biorxiv.org/content/biorxiv/early/2018/04/11/298661.full.pdf
    """,
    author="Kevin Wang",
    author_email="kevin@spikegadgets.com",
    packages=find_packages(),
    install_requires=["cffi>=1.0.0"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=[
        "./ripple/build.py:ffibuilder",
    ],
)
