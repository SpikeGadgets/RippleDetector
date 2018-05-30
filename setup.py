#!/usr/bin/python3
# Copyright (C) 2018 SpikeGadgets, Kevin Wang kevin@spikegadgets.com

# This program is free software: you can redistribute it and/or modify
#                                it under the terms of the GNU General Public License as published by
#                                the Free Software Foundation, either version 3 of the License, or
#                                (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
