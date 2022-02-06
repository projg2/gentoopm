#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..basepm.contents import PMPackageContents, PMContentObj


class PaludisPackageContents(PMPackageContents):
    def __init__(self, cont):
        self._cont = cont

    def __iter__(self):
        for f in self._cont:
            yield PMContentObj(f.location_key().parse_value())
