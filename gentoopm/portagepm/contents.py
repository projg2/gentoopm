# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

from ..basepm.contents import PMPackageContents, PMContentObj


class PortagePackageContents(PMPackageContents):
    def __init__(self, dblink):
        self._dblink = dblink

    def __iter__(self):
        for f, details in self._dblink.getcontents().items():
            yield PMContentObj(str(f))
