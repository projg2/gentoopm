# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

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
