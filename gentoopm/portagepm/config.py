#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.data

from ..basepm.config import PMConfig


class PortageConfig(PMConfig):
    def __init__(self, settings):
        self._settings = settings

    @property
    def userpriv_enabled(self):
        return "userpriv" in self._settings.features

    @property
    def userpriv_uid(self):
        return portage.data.portage_uid

    @property
    def userpriv_gid(self):
        return portage.data.portage_gid
