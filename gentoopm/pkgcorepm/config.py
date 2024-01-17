# (c) 2017-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

import os

import pkgcore.os_data

from ..basepm.config import PMConfig


class PkgCoreConfig(PMConfig):
    def __init__(self, domain):
        self._domain = domain

    @property
    def userpriv_enabled(self):
        return "userpriv" in self._domain.settings["FEATURES"] and os.getuid() == 0

    @property
    def userpriv_uid(self):
        return pkgcore.os_data.portage_uid

    @property
    def userpriv_gid(self):
        return pkgcore.os_data.portage_gid
