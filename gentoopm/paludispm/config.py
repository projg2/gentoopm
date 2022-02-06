#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..basepm.config import PMConfig


class PaludisConfig(PMConfig):
    def __init__(self, env):
        self._env = env

    # XXX: the userpriv_* funcs return current UID/GID
    # when run by an unprivileged user

    @property
    def userpriv_enabled(self):
        return self.userpriv_uid != 0

    @property
    def userpriv_uid(self):
        return self._env.reduced_uid()

    @property
    def userpriv_gid(self):
        return self._env.reduced_gid()
