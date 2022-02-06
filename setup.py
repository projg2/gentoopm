#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from distutils.core import setup, Command

import errno, os, os.path, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
try:
    from gentoopm import PV
except ImportError:
    PV = "unknown"


setup(
    name="gentoopm",
    version=PV,
    author="Michał Górny",
    author_email="mgorny@gentoo.org",
    url="https://github.com/mgorny/gentoopm/",
    packages=[
        "gentoopm",
        "gentoopm.basepm",
        "gentoopm.bash",
        "gentoopm.paludispm",
        "gentoopm.pkgcorepm",
        "gentoopm.portagepm",
        "gentoopm.tests",
    ],
    scripts=["gentoopmq"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
    ],
)
