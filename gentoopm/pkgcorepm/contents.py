# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

from ..basepm.contents import PMPackageContents, PMContentObj


class PkgCorePackageContents(PMPackageContents):
    def __init__(self, cont):
        self._cont = cont

    def __iter__(self):
        for f in self._cont:
            yield PMContentObj(f.location)

    def __contains__(self, path):
        return str(path) in self._cont
