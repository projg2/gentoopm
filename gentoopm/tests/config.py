#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from . import PMTestCase


class ConfigTestCase(PMTestCase):
    def setUp(self):
        self._conf = self.pm.config

    def test_userpriv(self):
        if self._conf.userpriv_enabled:
            # root's no userpriv
            self.assertNotEqual(self._conf.userpriv_uid, 0)
            self.assertNotEqual(self._conf.userpriv_gid, 0)

    def tearDown(self):
        pass
