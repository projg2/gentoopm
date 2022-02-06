#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2017 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

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
