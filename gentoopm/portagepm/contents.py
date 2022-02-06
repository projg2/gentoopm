#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..basepm.contents import PMPackageContents, PMContentObj


class PortagePackageContents(PMPackageContents):
    def __init__(self, dblink):
        self._dblink = dblink

    def __iter__(self):
        for f, details in self._dblink.getcontents().items():
            yield PMContentObj(str(f))
